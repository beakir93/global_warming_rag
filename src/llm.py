from __future__ import annotations

from functools import lru_cache

from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat.embeddings import GigaChatEmbeddings

from src.config import (
    GIGACHAT_CREDENTIALS,
    GIGACHAT_MODEL,
    GIGACHAT_SCOPE,
    GIGACHAT_VISION_MODEL,
)


@lru_cache(maxsize=1)
def build_llm() -> GigaChat:
    return GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        model=GIGACHAT_MODEL,
        verify_ssl_certs=False,
        timeout=120,
        profanity_check=False,
    )


@lru_cache(maxsize=1)
def build_vision_llm() -> GigaChat:
    return GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        model=GIGACHAT_VISION_MODEL,
        verify_ssl_certs=False,
        timeout=120,
        profanity_check=False,
    )


@lru_cache(maxsize=1)
def build_embeddings() -> GigaChatEmbeddings:
    return GigaChatEmbeddings(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        verify_ssl_certs=False,
    )
