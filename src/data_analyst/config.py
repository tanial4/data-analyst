"""Application configuration, loaded from environment variables / a .env file.

Replaces the Colab-specific ``google.colab.userdata`` secret lookup.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Values come from environment variables or a ``.env``
    file at the project root (case-insensitive, e.g. ``GROQ_API_KEY``)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- LLM ---------------------------------------------------------------
    groq_api_key: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.0

    # --- Agent loop --------------------------------------------------------
    max_agent_iterations: int = 6

    # --- UI ----------------------------------------------------------------
    share: bool = False
    server_name: str = "127.0.0.1"
    server_port: int = 7860
    show_error: bool = True


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a process-wide cached :class:`Settings` instance."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]  # values from env/.env
    return _settings
