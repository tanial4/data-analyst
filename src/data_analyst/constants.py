"""Single source of truth for the vocabularies shared across the agent, the
operation executor and the chart engine.

The original Colab notebook duplicated these lists in three places (the planner
prompt, the executor branches and the agg-func whitelist), which made them easy
to drift apart. Importing from here keeps them in sync.
"""

from __future__ import annotations

# Analytical operations the executor knows how to run.
OPERATIONS: tuple[str, ...] = (
    "summary",
    "average",
    "sum",
    "count",
    "min",
    "max",
    "median",
    "top_n",
    "groupby_agg",
    "distribution",
    "correlation",
    "list_unique",
    "full_stats",
)

# Aggregation functions accepted by groupby_agg.
AGG_FUNCS: tuple[str, ...] = ("mean", "sum", "count", "min", "max", "median", "std", "var")

# Chart types the chart engine can render. "none" means "no chart".
CHART_TYPES: tuple[str, ...] = (
    "none",
    "bar",
    "line",
    "pie",
    "donut",
    "histogram",
    "scatter",
    "box",
    "area",
    "heatmap",
)

# Chart types that consume the *raw* dataset (a single/related column) rather
# than an already-aggregated result table.
RAW_DATA_CHARTS: frozenset[str] = frozenset({"histogram", "box", "scatter", "heatmap"})

# Comparison operators supported by the filter engine.
FILTER_OPERATORS: tuple[str, ...] = ("==", "!=", ">", "<", ">=", "<=", "contains")
