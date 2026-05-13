from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from langchain_core.documents import Document
from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi

from src.config import CHROMA_DIR, COLLECTION_NAME, DEFAULT_RRF_K
from src.llm import build_embeddings

_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


@dataclass
class RetrievedDoc:
    document: Document
    score: float
    sources: dict


def build_vectorstore(documents: list[Document]) -> Chroma:
    embeddings = build_embeddings()
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    if store._collection.count() == 0:
        store.add_documents(documents)
    return store


def load_vectorstore() -> Chroma:
    embeddings = build_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def reset_vectorstore() -> None:
    embeddings = build_embeddings()
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    try:
        store.delete_collection()
    except Exception:
        pass


class HybridRetriever:
    def __init__(
        self,
        vectorstore: Chroma,
        documents: list[Document],
        rrf_k: int = DEFAULT_RRF_K,
    ) -> None:
        self.vectorstore = vectorstore
        self.documents = documents
        self.rrf_k = rrf_k
        self._id_to_pos: dict[str, int] = {
            doc.metadata.get("doc_id", str(i)): i for i, doc in enumerate(documents)
        }
        tokenized = [tokenize(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(tokenized) if any(tokenized) else None

    def _rrf(self, rank: int) -> float:
        return 1.0 / (self.rrf_k + rank)

    def _dense_ranking(self, query: str) -> list[tuple[int, float]]:
        results = self.vectorstore.similarity_search_with_score(
            query, k=len(self.documents)
        )
        rankings: list[tuple[int, float]] = []
        for rank, (doc, _score) in enumerate(results, start=1):
            doc_id = doc.metadata.get("doc_id")
            pos = self._id_to_pos.get(doc_id)
            if pos is None:
                continue
            rankings.append((pos, self._rrf(rank)))
        return rankings

    def _sparse_ranking(self, query: str) -> list[tuple[int, float]]:
        if self.bm25 is None:
            return []
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        order = np.argsort(scores)[::-1]
        return [(int(pos), self._rrf(rank)) for rank, pos in enumerate(order, start=1)]

    def search(
        self,
        query: str,
        k: int = 5,
        modality_filter: str | None = None,
        additional_context_chunks: list[str] | None = None,
    ) -> list[RetrievedDoc]:
        fused: dict[int, float] = {}
        
        # Стандартный поиск по векторной базе (Dense + Sparse)
        for pos, score in self._dense_ranking(query):
            fused[pos] = fused.get(pos, 0.0) + score
        for pos, score in self._sparse_ranking(query):
            fused[pos] = fused.get(pos, 0.0) + score

        # Если есть дополнительные чанки из загруженного файла, добавляем их с высоким приоритетом
        if additional_context_chunks:
            # Создаем временные документы для дополнительных чанков
            # Они не находятся в self.documents, поэтому мы их обрабатываем отдельно
            # и возвращаем как часть результатов с максимальным скором
            pass  # Логика обработки вынесена в класс-обертку или UI слой
        
        ordered = sorted(fused.items(), key=lambda x: x[1], reverse=True)
        out: list[RetrievedDoc] = []
        for pos, score in ordered:
            doc = self.documents[pos]
            if modality_filter and doc.metadata.get("modality") != modality_filter:
                continue
            out.append(
                RetrievedDoc(
                    document=doc,
                    score=score,
                    sources={
                        "modality": doc.metadata.get("modality"),
                        "doc_id": doc.metadata.get("doc_id"),
                    },
                )
            )
            if len(out) >= k:
                break
        return out


def build_documents(
    transcript_chunks: list[dict],
    frame_captions: list[dict],
) -> list[Document]:
    documents: list[Document] = []
    for chunk in transcript_chunks:
        meta = {
            "modality": "text",
            "doc_id": f"text-{chunk['chunk_id']}",
            "chunk_id": chunk["chunk_id"],
            "start_sentence": chunk["start_sentence"],
            "end_sentence": chunk["end_sentence"],
            "start_time": chunk.get("start_time", 0.0),
            "end_time": chunk.get("end_time", 0.0),
        }
        documents.append(Document(page_content=chunk["text"], metadata=meta))

    for frame in frame_captions:
        caption = frame.get("caption", "")
        if not caption:
            continue
        meta = {
            "modality": "frame",
            "doc_id": f"frame-{frame['index']}",
            "frame_index": frame["index"],
            "timestamp": frame.get("timestamp", 0.0),
            "abs_path": frame.get("abs_path", ""),
        }
        documents.append(
            Document(
                page_content=f"[Кадр в {frame.get('timestamp', 0):.0f} сек] {caption}",
                metadata=meta,
            )
        )

    return documents


def iter_documents(documents: list[Document]) -> Iterable[Document]:
    return documents
