from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import cv2

from src.config import (
    FRAME_INTERVAL_SEC,
    FRAMES_DIR,
    TRANSCRIPT_PATH,
    VIDEO_PATH,
    YOUTUBE_URL,
)


def _has_executable(name: str) -> bool:
    return shutil.which(name) is not None


class VideoDownloadError(RuntimeError):
    pass


def download_video(
    url: str = YOUTUBE_URL,
    target: Path = VIDEO_PATH,
    cookies_from_browser: str | None = None,
) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return target

    base_args = [
        "--remote-components",
        "ejs:github",
        "-f",
        "mp4/bestvideo[ext=mp4]+bestaudio/best/best",
        "--merge-output-format",
        "mp4",
        "-o",
        str(target),
        url,
    ]
    if cookies_from_browser:
        base_args = ["--cookies-from-browser", cookies_from_browser, *base_args]

    if _has_executable("yt-dlp"):
        cmd = ["yt-dlp", *base_args]
    else:
        cmd = [sys.executable, "-m", "yt_dlp", *base_args]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        raise VideoDownloadError(
            "Не удалось скачать видео через yt-dlp (вероятно, YouTube требует "
            "авторизации). Скачайте видео вручную и положите его в data/video.mp4, "
            "затем перезапустите prepare_data.py."
        ) from exc
    return target


def extract_frames(
    video_path: Path = VIDEO_PATH,
    frames_dir: Path = FRAMES_DIR,
    interval_sec: float = FRAME_INTERVAL_SEC,
) -> list[dict]:
    frames_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps else 0.0

    step = max(1, int(round(interval_sec * fps)))
    records: list[dict] = []
    index = 0

    frame_id = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_id % step == 0:
            timestamp = frame_id / fps if fps else 0.0
            filename = frames_dir / f"frame_{index:04d}_{int(timestamp):04d}s.jpg"
            cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 88])
            records.append(
                {
                    "index": index,
                    "timestamp": round(timestamp, 2),
                    "path": str(filename.relative_to(filename.parent.parent.parent)),
                    "abs_path": str(filename),
                }
            )
            index += 1
        frame_id += 1

    capture.release()

    if not records:
        raise RuntimeError("No frames extracted")

    for record in records:
        record["duration"] = round(duration, 2)
        record["interval_sec"] = float(interval_sec)
    return records


def _split_sentences(text: str) -> list[str]:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[\.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _join(parts: Iterable[str]) -> str:
    return " ".join(parts).strip()


def load_transcript_chunks(
    path: Path = TRANSCRIPT_PATH,
    sentences_per_chunk: int = 3,
    overlap: int = 1,
) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    sentences = _split_sentences(raw)
    if not sentences:
        return []

    chunks: list[dict] = []
    step = max(1, sentences_per_chunk - overlap)
    for i in range(0, len(sentences), step):
        window = sentences[i : i + sentences_per_chunk]
        if not window:
            continue
        chunks.append(
            {
                "chunk_id": len(chunks),
                "text": _join(window),
                "start_sentence": i,
                "end_sentence": i + len(window) - 1,
            }
        )
        if i + sentences_per_chunk >= len(sentences):
            break

    return chunks


def assign_chunk_timestamps(
    chunks: list[dict],
    video_duration: float,
    total_sentences: int,
) -> list[dict]:
    if total_sentences <= 0 or video_duration <= 0:
        return chunks
    per_sentence = video_duration / total_sentences
    for chunk in chunks:
        start = chunk["start_sentence"] * per_sentence
        end = (chunk["end_sentence"] + 1) * per_sentence
        chunk["start_time"] = round(start, 2)
        chunk["end_time"] = round(end, 2)
    return chunks


def transcript_sentence_count(path: Path = TRANSCRIPT_PATH) -> int:
    return len(_split_sentences(path.read_text(encoding="utf-8")))
