from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.captions import caption_frames, load_captions
from src.config import (
    CAPTIONS_PATH,
    FRAMES_DIR,
    INDEX_META_PATH,
    TRANSCRIPT_PATH,
    VIDEO_PATH,
)
from src.ingest import (
    VideoDownloadError,
    assign_chunk_timestamps,
    download_video,
    extract_frames,
    load_transcript_chunks,
    transcript_sentence_count,
)
from src.retriever import build_documents, build_vectorstore, reset_vectorstore


def _existing_frames() -> list[dict]:
    files = sorted(FRAMES_DIR.glob("frame_*.jpg"))
    records: list[dict] = []
    for idx, path in enumerate(files):
        stem = path.stem
        try:
            ts = int(stem.split("_")[-1].rstrip("s"))
        except ValueError:
            ts = 0
        records.append(
            {
                "index": idx,
                "timestamp": float(ts),
                "abs_path": str(path),
                "path": str(path.relative_to(path.parent.parent.parent)),
            }
        )
    return records


def run(force: bool = False, cookies_from_browser: str | None = None) -> None:
    if force:
        if VIDEO_PATH.exists():
            VIDEO_PATH.unlink()
        for f in FRAMES_DIR.glob("frame_*.jpg"):
            f.unlink()
        if CAPTIONS_PATH.exists():
            CAPTIONS_PATH.unlink()
        if INDEX_META_PATH.exists():
            INDEX_META_PATH.unlink()
        reset_vectorstore()

    print("[1/5] Скачивание видео...")
    video_available = True
    try:
        video_path = download_video(cookies_from_browser=cookies_from_browser)
        print(f"      Видео: {video_path}")
    except VideoDownloadError as exc:
        video_available = False
        print(f"      [пропуск] {exc}")

    frames: list[dict] = []
    captioned: list[dict] = []

    print("[2/5] Извлечение кадров...")
    if any(FRAMES_DIR.glob("frame_*.jpg")) and not force:
        frames = _existing_frames()
        print(f"      Найдено {len(frames)} существующих кадров")
    elif video_available and VIDEO_PATH.exists():
        frames = extract_frames(VIDEO_PATH)
        print(f"      Извлечено {len(frames)} кадров")
    else:
        print("      [пропуск] видео недоступно, индекс будет только из текста")

    print("[3/5] Описание кадров через GigaChat Vision...")
    if frames:
        captioned = caption_frames(frames)
        captioned = [
            c
            for c in captioned
            if c.get("caption") and not c["caption"].startswith("[caption unavailable")
        ]
        print(f"      Описано {len(captioned)} кадров")
    else:
        print("      [пропуск] нет кадров для описания")

    print("[4/5] Разбиение транскрипции на чанки...")
    chunks = load_transcript_chunks(TRANSCRIPT_PATH)
    duration = max((c.get("timestamp", 0) for c in load_captions()), default=0.0)
    duration = max(duration, max((f.get("timestamp", 0) for f in frames), default=0.0))
    chunks = assign_chunk_timestamps(
        chunks,
        video_duration=duration,
        total_sentences=transcript_sentence_count(TRANSCRIPT_PATH),
    )
    print(f"      Получено {len(chunks)} чанков транскрипции")

    print("[5/5] Построение векторного индекса (Chroma + GigaChat Embeddings)...")
    reset_vectorstore()
    documents = build_documents(chunks, captioned)
    build_vectorstore(documents)
    print(f"      Проиндексировано {len(documents)} документов")

    INDEX_META_PATH.write_text(
        json.dumps(
            {
                "transcript_chunks": len(chunks),
                "frames": len(captioned),
                "video_duration_sec": duration,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Готово. Запустите интерфейс: streamlit run app.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Подготовка данных мультимодальной RAG")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Пересоздать видео, кадры, описания и индекс с нуля",
    )
    parser.add_argument(
        "--cookies-from-browser",
        default=None,
        help="Имя браузера для yt-dlp (safari, chrome, firefox и т.п.)",
    )
    args = parser.parse_args()
    run(force=args.force, cookies_from_browser=args.cookies_from_browser)


if __name__ == "__main__":
    main()
