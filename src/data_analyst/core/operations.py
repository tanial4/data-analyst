"""Deterministic analytical operations over a DataFrame.

This is the refactored core of the notebook's ``execute_plan``. Each operation
is a small function returning an :class:`OperationResult` (a prose answer plus a
result table). Charting is intentionally *not* done here — in the agent
architecture the model decides separately whether to call ``create_chart`` on
the result, so computation and visualization stay decoupled.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from ..constants import AGG_FUNCS
from .filters import apply_filters
from .helpers import fmt, pick_cat, pick_num


@dataclass
class OperationResult:
    """Outcome of one analytical operation."""

    answer: str
    table: pd.DataFrame = field(default_factory=pd.DataFrame)


def run_operation(
    df: pd.DataFrame,
    operation: str,
    *,
    target_column: str | None = None,
    groupby_column: str | None = None,
    agg_func: str = "mean",
    top_n: int = 10,
    sort_order: str = "desc",
    filters: list[dict[str, Any]] | None = None,
) -> OperationResult:
    """Apply optional filters then dispatch to the requested operation."""
    wdf = apply_filters(df, filters)
    if wdf.empty:
        return OperationResult("No rows match the applied filters.")

    handler = _DISPATCH.get(operation)
    if handler is None:
        return OperationResult(f"Operation '{operation}' is not recognized.")

    return handler(
        wdf,
        target_column=target_column,
        groupby_column=groupby_column,
        agg_func=agg_func,
        top_n=top_n,
        sort_order=sort_order,
    )


# ---------------------------------------------------------------------------
# Individual operations. Each accepts the filtered DataFrame plus the full set
# of keyword params (ignoring those it does not need) and returns a result.
# ---------------------------------------------------------------------------


def _op_summary(wdf: pd.DataFrame, **_: Any) -> OperationResult:
    num_cols = wdf.select_dtypes(include="number").columns.tolist()
    stats = []
    for col in num_cols[:8]:
        s = wdf[col].dropna()
        stats.append(
            {
                "Column": col,
                "Count": int(s.count()),
                "Mean": round(s.mean(), 4),
                "Median": round(s.median(), 4),
                "Std": round(s.std(), 4),
                "Min": round(s.min(), 4),
                "Max": round(s.max(), 4),
            }
        )
    if stats:
        table = pd.DataFrame(stats)
    else:
        table = pd.DataFrame(
            {
                "Info": [
                    f"Rows: {len(wdf)}",
                    f"Columns: {len(wdf.columns)}",
                    f"Total nulls: {int(wdf.isna().sum().sum())}",
                ]
            }
        )
    missing = int(wdf.isna().sum().sum())
    answer = (
        f"The dataset has {len(wdf):,} rows and {len(wdf.columns)} columns. "
        f"Total null values: {missing}. Statistical summary of numeric columns shown below."
    )
    return OperationResult(answer, table)


def _op_scalar(wdf: pd.DataFrame, operation: str, target_column: str | None, **_: Any) -> OperationResult:
    target = target_column if (target_column and target_column in wdf.columns) else pick_num(wdf)
    if target is None:
        return OperationResult("Could not find a valid numeric column.")
    num_s = pd.to_numeric(wdf[target], errors="coerce")
    ops_map = {
        "average": ("Mean", num_s.mean()),
        "sum": ("Sum", num_s.sum()),
        "count": ("Count", int(num_s.count())),
        "min": ("Min", num_s.min()),
        "max": ("Max", num_s.max()),
        "median": ("Median", num_s.median()),
    }
    label, value = ops_map[operation]
    table = pd.DataFrame({"Metric": [label], "Column": [target], "Value": [value]})
    return OperationResult(f"{label} of '{target}': {fmt(value)}", table)


def _op_full_stats(wdf: pd.DataFrame, target_column: str | None, **_: Any) -> OperationResult:
    target = target_column if (target_column and target_column in wdf.columns) else pick_num(wdf)
    if target is None:
        return OperationResult("Could not find a valid numeric column.")
    s = pd.to_numeric(wdf[target], errors="coerce").dropna()
    table = pd.DataFrame(
        list(
            {
                "Count": int(s.count()),
                "Mean": round(s.mean(), 4),
                "Median": round(s.median(), 4),
                "Mode": round(s.mode().iloc[0], 4) if not s.mode().empty else "N/A",
                "Std Dev": round(s.std(), 4),
                "Variance": round(s.var(), 4),
                "Min": round(s.min(), 4),
                "Q1": round(s.quantile(0.25), 4),
                "Q3": round(s.quantile(0.75), 4),
                "Max": round(s.max(), 4),
                "IQR": round(s.quantile(0.75) - s.quantile(0.25), 4),
                "Skewness": round(s.skew(), 4),
                "Kurtosis": round(s.kurt(), 4),
            }.items()
        ),
        columns=["Statistic", "Value"],
    )
    return OperationResult(f"Full statistics for '{target}'.", table)


def _op_top_n(
    wdf: pd.DataFrame, target_column: str | None, top_n: int, sort_order: str, **_: Any
) -> OperationResult:
    sort_col = target_column if (target_column and target_column in wdf.columns) else pick_num(wdf)
    if sort_col is None:
        return OperationResult("No valid column found for sorting.")
    asc = sort_order == "asc"
    table = wdf.sort_values(by=sort_col, ascending=asc).head(int(top_n)).copy()
    label = "lowest" if asc else "highest"
    return OperationResult(
        f"Top {int(top_n)} rows with the {label} values in '{sort_col}'.", table
    )


def _op_groupby_agg(
    wdf: pd.DataFrame,
    target_column: str | None,
    groupby_column: str | None,
    agg_func: str,
    sort_order: str,
    **_: Any,
) -> OperationResult:
    groupby = groupby_column if (groupby_column and groupby_column in wdf.columns) else pick_cat(wdf)
    if groupby is None:
        return OperationResult("No valid categorical column found for grouping.")
    target = target_column if (target_column and target_column in wdf.columns) else pick_num(wdf)
    if agg_func not in AGG_FUNCS:
        agg_func = "count" if target is None else "mean"
    if agg_func == "count" or target is None:
        grouped = wdf.groupby(groupby, dropna=False).size().reset_index(name="count")
        metric_col = "count"
    else:
        grouped = wdf.groupby(groupby, dropna=False)[target].agg(agg_func).reset_index()
        grouped.columns = [groupby, f"{agg_func}_{target}"]
        metric_col = f"{agg_func}_{target}"
    if sort_order in ("asc", "desc"):
        grouped = grouped.sort_values(metric_col, ascending=(sort_order == "asc"))
    answer = (
        f"{agg_func.capitalize()} of '{target or 'count'}' grouped by '{groupby}'. "
        f"Found {len(grouped)} groups. (group column: '{groupby}', metric column: '{metric_col}')"
    )
    return OperationResult(answer, grouped.copy())


def _op_distribution(wdf: pd.DataFrame, target_column: str | None, **_: Any) -> OperationResult:
    target = target_column if (target_column and target_column in wdf.columns) else pick_num(wdf)
    if target is None:
        return OperationResult("No numeric column found for distribution analysis.")
    s = pd.to_numeric(wdf[target], errors="coerce").dropna()
    table = pd.DataFrame(
        {
            "Statistic": ["Count", "Mean", "Median", "Std", "Min", "Max"],
            "Value": [s.count(), s.mean(), s.median(), s.std(), s.min(), s.max()],
        }
    )
    answer = (
        f"Distribution of '{target}': mean = {fmt(s.mean())}, "
        f"median = {fmt(s.median())}, std = {fmt(s.std())}."
    )
    return OperationResult(answer, table)


def _op_correlation(
    wdf: pd.DataFrame, target_column: str | None, groupby_column: str | None, **_: Any
) -> OperationResult:
    num_cols = wdf.select_dtypes(include="number").columns.tolist()
    # Allow the caller to name the two columns via target/groupby; otherwise use
    # the first two numeric columns.
    x_col = target_column if (target_column and target_column in num_cols) else (num_cols[0] if num_cols else None)
    y_col = groupby_column if (groupby_column and groupby_column in num_cols) else (
        num_cols[1] if len(num_cols) >= 2 else None
    )
    if not x_col or not y_col or x_col == y_col:
        if len(num_cols) >= 2:
            table = wdf[num_cols].corr().round(4)
            return OperationResult("Correlation matrix between all numeric variables.", table)
        return OperationResult("Need at least two numeric columns for correlation.")

    tmp = wdf[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()
    corr_val = tmp[x_col].corr(tmp[y_col])
    strength = (
        "very strong" if abs(corr_val) > 0.8 else
        "strong" if abs(corr_val) > 0.6 else
        "moderate" if abs(corr_val) > 0.4 else "weak"
    )
    direction = "positive" if corr_val > 0 else "negative"
    table = pd.DataFrame(
        {
            "Variable X": [x_col],
            "Variable Y": [y_col],
            "Correlation (r)": [round(corr_val, 4)],
            "Interpretation": [f"{strength} {direction}"],
        }
    )
    answer = (
        f"Correlation between '{x_col}' and '{y_col}': "
        f"r = {fmt(corr_val)} ({strength} {direction})."
    )
    return OperationResult(answer, table)


def _op_list_unique(wdf: pd.DataFrame, target_column: str | None, **_: Any) -> OperationResult:
    target = target_column if (target_column and target_column in wdf.columns) else pick_cat(wdf)
    if target is None:
        return OperationResult("No categorical column found.")
    uniques = wdf[target].dropna().astype(str).unique().tolist()
    table = pd.DataFrame({target: sorted(uniques)[:200]})
    return OperationResult(f"'{target}' has {len(uniques)} unique values.", table)


_DISPATCH = {
    "summary": _op_summary,
    "average": lambda wdf, **kw: _op_scalar(wdf, "average", kw.get("target_column")),
    "sum": lambda wdf, **kw: _op_scalar(wdf, "sum", kw.get("target_column")),
    "count": lambda wdf, **kw: _op_scalar(wdf, "count", kw.get("target_column")),
    "min": lambda wdf, **kw: _op_scalar(wdf, "min", kw.get("target_column")),
    "max": lambda wdf, **kw: _op_scalar(wdf, "max", kw.get("target_column")),
    "median": lambda wdf, **kw: _op_scalar(wdf, "median", kw.get("target_column")),
    "full_stats": _op_full_stats,
    "top_n": _op_top_n,
    "groupby_agg": _op_groupby_agg,
    "distribution": _op_distribution,
    "correlation": _op_correlation,
    "list_unique": _op_list_unique,
}
