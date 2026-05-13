from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import build_llm
from src.retriever import HybridRetriever, RetrievedDoc

SYSTEM_PROMPT = (
    "Ты — экспертный ассистент по теме глобального потепления. "
    "Отвечай строго на основе предоставленного контекста: текстовых фрагментов "
    "транскрипции видео и описаний кадров. Если данных недостаточно, честно скажи "
    "об этом и не выдумывай факты. Структурируй ответ списком или короткими "
    "абзацами, ссылайся на источники в формате [T#] для текста и [F#] для кадров."
)

HYDE_PROMPT = (
    "Сформулируй короткий гипотетический ответ (3–4 предложения) на следующий "
    "вопрос про глобальное потепление. Пиши уверенно и фактологично, как будто "
    "это выдержка из научного отчёта. Не используй вводные фразы.\n\nВопрос: {query}"
)


@dataclass
class RagAnswer:
    question: str
    answer: str
    contexts: list[RetrievedDoc]
    hypothetical: Optional[str] = None
    frames: list[dict] = field(default_factory=list)


def hyde_expand(query: str) -> str:
    llm = build_llm()
    prompt = HYDE_PROMPT.format(query=query)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def _format_context(items: list[RetrievedDoc]) -> str:
    blocks: list[str] = []
    text_idx = 1
    frame_idx = 1
    for item in items:
        meta = item.document.metadata
        if meta.get("modality") == "text":
            tag = f"T{text_idx}"
            text_idx += 1
            header = f"[{tag}] фрагмент транскрипции (~{meta.get('start_time', 0):.0f}–{meta.get('end_time', 0):.0f} сек)"
        else:
            tag = f"F{frame_idx}"
            frame_idx += 1
            header = f"[{tag}] описание кадра (t={meta.get('timestamp', 0):.0f} сек)"
        blocks.append(f"{header}\n{item.document.page_content}")
    return "\n\n".join(blocks)


def _tag_contexts(items: list[RetrievedDoc]) -> list[RetrievedDoc]:
    text_idx = 1
    frame_idx = 1
    tagged: list[RetrievedDoc] = []
    for item in items:
        meta = dict(item.document.metadata)
        if meta.get("modality") == "text":
            meta["citation"] = f"T{text_idx}"
            text_idx += 1
        else:
            meta["citation"] = f"F{frame_idx}"
            frame_idx += 1
        item.document.metadata = meta
        tagged.append(item)
    return tagged


def answer_query(
    retriever: HybridRetriever,
    question: str,
    top_k: int = 6,
    use_hyde: bool = True,
    text_quota: int = 4,
    frame_quota: int = 3,
) -> RagAnswer:
    search_query = question
    hypothetical: Optional[str] = None
    if use_hyde:
        hypothetical = hyde_expand(question)
        search_query = f"{question}\n\n{hypothetical}"

    text_hits = retriever.search(search_query, k=text_quota, modality_filter="text")
    frame_hits = retriever.search(search_query, k=frame_quota, modality_filter="frame")

    merged: list[RetrievedDoc] = []
    seen: set[str] = set()
    for item in text_hits + frame_hits:
        doc_id = item.document.metadata.get("doc_id")
        if doc_id in seen:
            continue
        seen.add(doc_id)
        merged.append(item)
        if len(merged) >= top_k:
            break

    merged = _tag_contexts(merged)
    context_text = _format_context(merged)

    llm = build_llm()
    user_prompt = (
        f"Вопрос пользователя: {question}\n\n"
        f"Контекст:\n{context_text}\n\n"
        "Дай развёрнутый, но компактный ответ на русском языке. "
        "Сошлись на использованные источники тегами вида [T1], [F2] и т.п. "
        "В конце добавь короткий итог одной фразой."
    )
    response = llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_prompt)]
    )

    frames = [
        {
            "abs_path": item.document.metadata.get("abs_path"),
            "timestamp": item.document.metadata.get("timestamp"),
            "citation": item.document.metadata.get("citation"),
            "caption": item.document.page_content,
        }
        for item in merged
        if item.document.metadata.get("modality") == "frame"
    ]

    return RagAnswer(
        question=question,
        answer=response.content.strip(),
        contexts=merged,
        hypothetical=hypothetical,
        frames=frames,
    )
