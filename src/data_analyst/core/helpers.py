"""Small shared utilities for formatting and column selection."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def fmt(value: Any) -> str:
    """Format a scalar for prose: ``N/A`` for None, ``NaN`` for missing,
    4 significant figures with thousands separators for floats."""
    if value is None:
        return "N/A"
    try:
        if isinstance(value, float):
            if math.isnan(value):
                return "NaN"
            return f"{value:,.4g}"
        if pd.isna(value):
            return "NaN"
    except Exception:
        pass
    return str(value)


def pick_num(df: pd.DataFrame) -> str | None:
    """First numeric column, or ``None``."""
    cols = df.select_dtypes(include="number").columns.tolist()
    return cols[0] if cols else None


def pick_cat(df: pd.DataFrame) -> str | None:
    """First categorical (text/category/bool) column, or ``None``."""
    cols = df.select_dtypes(include=["object", "string", "category", "bool"]).columns.tolist()
    return cols[0] if cols else None
