"""Row filtering applied before any analytical operation."""

from __future__ import annotations

from typing import Any

import pandas as pd


def apply_filters(df: pd.DataFrame, filters: list[dict[str, Any]] | None) -> pd.DataFrame:
    """Return a copy of ``df`` with the given filters applied.

    Each filter is a dict ``{"column", "operator", "value"}``. Unknown columns
    and malformed filters are skipped silently so a bad filter never aborts an
    analysis. Comparison operators (>, <, >=, <=) coerce both sides to numeric.
    """
    out = df.copy()
    for f in filters or []:
        col = f.get("column")
        op = f.get("operator")
        val = f.get("value")
        if col not in out.columns:
            continue
        try:
            s = out[col]
            if op == "==":
                out = out[s == val]
            elif op == "!=":
                out = out[s != val]
            elif op == "contains":
                # regex=False: treat the value as a literal substring. Pandas
                # defaults to regex=True, which would let a crafted filter value
                # inject a regex (ReDoS / errors) from untrusted data.
                out = out[s.astype(str).str.contains(str(val), case=False, na=False, regex=False)]
            else:
                num_val = float(val)
                num_s = pd.to_numeric(s, errors="coerce")
                if op == ">":
                    out = out[num_s > num_val]
                elif op == "<":
                    out = out[num_s < num_val]
                elif op == ">=":
                    out = out[num_s >= num_val]
                elif op == "<=":
                    out = out[num_s <= num_val]
        except Exception:
            continue
    return out
