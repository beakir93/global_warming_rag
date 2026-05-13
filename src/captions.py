from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Iterable

from gigachat import GigaChat as RawGigaChat
from gigachat.models import Chat, Messages, MessagesRole
from tqdm import tqdm

from src.config import (
    CAPTIONS_PATH,
    GIGACHAT_CREDENTIALS,
    GIGACHAT_SCOPE,
    GIGACHAT_VISION_MODEL,
)

CAPTION_INSTRUCTION = (
    "Опиши коротко (2–3 предложения) что изображено на кадре из научно-популярного "
    "видео про глобальное потепление. Сосредоточься на видимых объектах, действиях, "
    "природных явлениях и подписях. Не выдумывай детали, которых не видно."
)


def _make_client() -> RawGigaChat:
    return RawGigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        model=GIGACHAT_VISION_MODEL,
        verify_ssl_certs=False,
        timeout=120,
    )


def _upload_image(client: RawGigaChat, path: Path) -> str:
    with open(path, "rb") as fh:
        uploaded = client.upload_file(
            file=(path.name, fh.read(), "image/jpeg"),
            purpose="general",
        )
    return uploaded.id_


def _caption_with_attachment(client: RawGigaChat, file_id: str) -> str:
    response = client.chat(
        Chat(
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=CAPTION_INSTRUCTION,
                    attachments=[file_id],
                )
            ],
            temperature=0.2,
        )
    )
    return response.choices[0].message.content.strip()


def _caption_with_base64(client: RawGigaChat, path: Path) -> str:
    image_bytes = path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    response = client.chat(
        Chat(
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=[
                        {"type": "text", "text": CAPTION_INSTRUCTION},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                        },
                    ],
                )
            ],
            temperature=0.2,
        )
    )
    return response.choices[0].message.content.strip()


def caption_frames(
    frames: Iterable[dict],
    out_path: Path = CAPTIONS_PATH,
) -> list[dict]:
    frames = list(frames)
    client = _make_client()
    results: list[dict] = []

    cached: dict[int, dict] = {}
    if out_path.exists():
        try:
            cached_list = json.loads(out_path.read_text(encoding="utf-8"))
            cached = {item["index"]: item for item in cached_list}
        except Exception:
            cached = {}

    try:
        for frame in tqdm(frames, desc="captioning"):
            if frame["index"] in cached and cached[frame["index"]].get("caption"):
                results.append(cached[frame["index"]])
                continue

            path = Path(frame["abs_path"])
            try:
                file_id = _upload_image(client, path)
                caption = _caption_with_attachment(client, file_id)
            except Exception:
                try:
                    caption = _caption_with_base64(client, path)
                except Exception as exc:
                    caption = f"[caption unavailable: {exc}]"

            record = dict(frame)
            record["caption"] = caption
            results.append(record)
            out_path.write_text(
                json.dumps(results, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    finally:
        try:
            client.close()
        except Exception:
            pass

    out_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return results


def load_captions(path: Path = CAPTIONS_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
