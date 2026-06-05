"""Per-conversation state.

Replaces the module-level ``STATE`` dict from the notebook with an instance so
that each Gradio session owns its own DataFrame and intermediate results
instead of sharing one global.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import pandas as pd

from .loader import build_schema


def _remove_quietly(path: str | None) -> None:
    if path:
        try:
            os.remove(path)
        except OSError:
            pass


@dataclass
class AnalystSession:
    """Holds the loaded dataset and the most recent analysis artifacts.

    ``last_table`` and ``last_chart_path`` are written by the agent's tools so a
    later ``create_chart`` call can chart the result of the preceding
    ``run_operation`` call, and so the UI can display them after a turn.
    """

    df: pd.DataFrame | None = None
    schema: str = ""
    filename: str = ""
    last_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    last_chart_path: str | None = None

    @property
    def has_data(self) -> bool:
        return self.df is not None

    def load(self, df: pd.DataFrame, filename: str) -> None:
        """Attach a freshly loaded DataFrame and reset prior artifacts."""
        self.df = df
        self.schema = build_schema(df)
        self.filename = filename
        self.last_table = pd.DataFrame()
        self.clear_chart()

    def set_chart(self, path: str | None) -> None:
        """Record a new chart, deleting the previous temp file to avoid disk leaks."""
        if path != self.last_chart_path:
            _remove_quietly(self.last_chart_path)
        self.last_chart_path = path

    def clear_chart(self) -> None:
        """Delete the current chart temp file and forget it."""
        _remove_quietly(self.last_chart_path)
        self.last_chart_path = None
