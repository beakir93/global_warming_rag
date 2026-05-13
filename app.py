from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.captions import load_captions
from src.config import (
    CAPTIONS_PATH,
    DEFAULT_TOP_K,
    INDEX_META_PATH,
    TRANSCRIPT_PATH,
    VIDEO_PATH,
)
from src.ingest import (
    assign_chunk_timestamps,
    load_transcript_chunks,
    transcript_sentence_count,
)
from src.rag import answer_query
from src.retriever import HybridRetriever, build_documents, load_vectorstore


st.set_page_config(
    page_title="Глобальное потепление — RAG-ассистент",
    page_icon="🌍",
    layout="wide",
)


@st.cache_resource(show_spinner="Поднимаю гибридный ретривер...")
def get_retriever() -> HybridRetriever:
    captions = load_captions(CAPTIONS_PATH)
    meta = {}
    if INDEX_META_PATH.exists():
        meta = json.loads(INDEX_META_PATH.read_text(encoding="utf-8"))

    chunks = load_transcript_chunks(TRANSCRIPT_PATH)
    duration = float(meta.get("video_duration_sec") or 0.0)
    if duration <= 0:
        duration = max((c.get("timestamp", 0) for c in captions), default=0.0)
    chunks = assign_chunk_timestamps(
        chunks,
        video_duration=duration,
        total_sentences=transcript_sentence_count(TRANSCRIPT_PATH),
    )
    documents = build_documents(chunks, captions)
    vectorstore = load_vectorstore()
    return HybridRetriever(vectorstore=vectorstore, documents=documents)


def _render_sidebar() -> dict:
    with st.sidebar:
        st.title("🌍 RAG по глобальному потеплению")
        st.caption("GigaChat-2-Max · GigaChat Embeddings · Chroma · BM25 · HyDE")

        st.subheader("Параметры запроса")
        top_k = st.slider("Итоговый top-K", 2, 10, DEFAULT_TOP_K)
        text_quota = st.slider("Текстовых фрагментов", 1, 8, 4)
        frame_quota = st.slider("Кадров", 0, 6, 3)
        use_hyde = st.toggle("HyDE-расширение запроса", value=True)

        st.divider()
        st.subheader("Источники")
        if INDEX_META_PATH.exists():
            meta = json.loads(INDEX_META_PATH.read_text(encoding="utf-8"))
            st.markdown(
                f"- Транскрипция: **{meta.get('transcript_chunks', 0)}** чанков\n"
                f"- Кадры: **{meta.get('frames', 0)}**\n"
                f"- Длительность видео: **{meta.get('video_duration_sec', 0):.1f} с**"
            )
        else:
            st.info("Сначала выполните `python prepare_data.py`.")

        if VIDEO_PATH.exists():
            with st.expander("Исходное видео"):
                st.video(str(VIDEO_PATH))

        with st.expander("Транскрипция (фрагмент)"):
            text = TRANSCRIPT_PATH.read_text(encoding="utf-8")
            st.text(text[:1200] + ("..." if len(text) > 1200 else ""))

    return {
        "top_k": top_k,
        "text_quota": text_quota,
        "frame_quota": frame_quota,
        "use_hyde": use_hyde,
    }


def _ensure_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []


def _render_frame_gallery(frames: list[dict]) -> None:
    if not frames:
        return
    cols = st.columns(min(3, len(frames)))
    for i, frame in enumerate(frames):
        path = frame.get("abs_path")
        if not path or not Path(path).exists():
            continue
        with cols[i % len(cols)]:
            ts = frame.get("timestamp") or 0
            citation = frame.get("citation") or ""
            st.image(path, caption=f"{citation} · t={ts:.0f}s", use_container_width=True)


def _render_context(contexts) -> None:
    text_items = [c for c in contexts if c.document.metadata.get("modality") == "text"]
    frame_items = [c for c in contexts if c.document.metadata.get("modality") == "frame"]

    with st.expander("📜 Текстовые фрагменты", expanded=False):
        for item in text_items:
            meta = item.document.metadata
            citation = meta.get("citation", "T?")
            st.markdown(
                f"**[{citation}] {meta.get('start_time', 0):.0f}–{meta.get('end_time', 0):.0f} сек · "
                f"score={item.score:.3f}**"
            )
            st.write(item.document.page_content)
            st.divider()

    with st.expander("🖼 Кадры", expanded=False):
        cols = st.columns(min(3, max(1, len(frame_items))))
        for i, item in enumerate(frame_items):
            meta = item.document.metadata
            path = meta.get("abs_path")
            with cols[i % len(cols)]:
                if path and Path(path).exists():
                    st.image(
                        path,
                        caption=f"{meta.get('citation','F?')} · t={meta.get('timestamp', 0):.0f}s · score={item.score:.3f}",
                        use_container_width=True,
                    )
                st.caption(item.document.page_content)


def main() -> None:
    _ensure_state()
    params = _render_sidebar()

    st.title("Мультимодальная RAG-система: глобальное потепление")
    st.caption(
        "Источники: расшифровка научно-популярного видео + описания ключевых кадров. "
        "Поиск — гибридный (Dense + BM25 + RRF), при необходимости с HyDE-расширением запроса."
    )

    if not INDEX_META_PATH.exists():
        st.warning("Индекс ещё не построен. Запустите `python prepare_data.py`.")
        st.stop()

    retriever = get_retriever()

    for turn in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(turn["question"])
        with st.chat_message("assistant"):
            st.markdown(turn["answer"])
            if turn.get("frames"):
                _render_frame_gallery(turn["frames"])
            if turn.get("hypothetical"):
                with st.expander("🧪 Гипотетический документ (HyDE)"):
                    st.write(turn["hypothetical"])
            if turn.get("contexts"):
                _render_context(turn["contexts"])

    question = st.chat_input("Спросите о глобальном потеплении...")
    if not question:
        return

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            result = answer_query(
                retriever,
                question,
                top_k=params["top_k"],
                use_hyde=params["use_hyde"],
                text_quota=params["text_quota"],
                frame_quota=params["frame_quota"],
            )
        st.markdown(result.answer)
        if result.frames:
            _render_frame_gallery(result.frames)
        if result.hypothetical:
            with st.expander("🧪 Гипотетический документ (HyDE)"):
                st.write(result.hypothetical)
        _render_context(result.contexts)

    st.session_state.history.append(
        {
            "question": question,
            "answer": result.answer,
            "frames": result.frames,
            "hypothetical": result.hypothetical,
            "contexts": result.contexts,
        }
    )


if __name__ == "__main__":
    main()
