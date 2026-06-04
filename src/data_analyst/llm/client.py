"""Factory for the Groq chat model."""

from __future__ import annotations

import os

from langchain_groq import ChatGroq

from ..config import get_settings


def get_llm() -> ChatGroq:
    """Build a :class:`ChatGroq` client from application settings.

    The Groq SDK reads ``GROQ_API_KEY`` from the environment, so we mirror the
    configured key there before constructing the client.
    """
    settings = get_settings()
    os.environ.setdefault("GROQ_API_KEY", settings.groq_api_key)
    return ChatGroq(model=settings.model, temperature=settings.temperature)
