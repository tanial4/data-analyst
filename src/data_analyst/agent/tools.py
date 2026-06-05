"""LangChain tools the agent can call, bound to a single :class:`AnalystSession`.

``build_tools(session)`` returns tools that close over the session so each
conversation operates on its own DataFrame. Tools return short text summaries to
the model and stash rich artifacts (the result DataFrame, the chart path) on the
session for the UI to display.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ..constants import CHART_TYPES, OPERATIONS, RAW_DATA_CHARTS
from ..charts.engine import make_chart
from ..core.operations import run_operation
from ..core.session import AnalystSession

_MAX_TABLE_ROWS_TO_MODEL = 20
_MAX_TABLE_COLS_TO_MODEL = 30


class RunOperationArgs(BaseModel):
    operation: str = Field(description=f"One of: {', '.join(OPERATIONS)}")
    target_column: str | None = Field(default=None, description="Primary column to analyze, if any")
    groupby_column: str | None = Field(default=None, description="Column to group by (groupby_agg only)")
    agg_func: str = Field(default="mean", description="Aggregation for groupby_agg: mean/sum/count/min/max/median/std/var")
    top_n: int = Field(default=10, description="Number of rows for top_n")
    sort_order: str = Field(default="desc", description="'asc' or 'desc'")
    filters_json: str | None = Field(
        default=None,
        description=(
            'Optional JSON array of row filters, e.g. '
            '[{"column":"region","operator":"==","value":"West"}]. '
            "Operators: ==, !=, >, <, >=, <=, contains."
        ),
    )


class CreateChartArgs(BaseModel):
    chart_type: str = Field(description=f"One of: {', '.join(c for c in CHART_TYPES if c != 'none')}")
    x: str | None = Field(default=None, description="Column for the x axis / categories")
    y: str | None = Field(default=None, description="Column for the y axis / values")
    title: str = Field(default="Analysis", description="Descriptive chart title")


def build_tools(session: AnalystSession) -> list[StructuredTool]:
    """Create the tool set bound to ``session``."""

    def get_schema() -> str:
        """Return the schema (columns, types, samples) of the loaded dataset."""
        if not session.has_data:
            return "No dataset is loaded."
        return session.schema

    def run_operation_tool(
        operation: str,
        target_column: str | None = None,
        groupby_column: str | None = None,
        agg_func: str = "mean",
        top_n: int = 10,
        sort_order: str = "desc",
        filters_json: str | None = None,
    ) -> str:
        """Run a deterministic analytical operation and return a text summary.

        The full result table is stored on the session for charting/display."""
        if not session.has_data:
            return "No dataset is loaded. Ask the user to upload a file."

        filters: list[dict[str, Any]] | None = None
        if filters_json:
            try:
                parsed = json.loads(filters_json)
                if isinstance(parsed, list):
                    filters = parsed
            except json.JSONDecodeError:
                return "filters_json was not valid JSON; omit it or fix the JSON array."

        result = run_operation(
            session.df,
            operation,
            target_column=target_column,
            groupby_column=groupby_column,
            agg_func=agg_func,
            top_n=top_n,
            sort_order=sort_order,
            filters=filters,
        )
        session.last_table = result.table

        if result.table.empty:
            return result.answer
        preview_df = result.table.iloc[:_MAX_TABLE_ROWS_TO_MODEL, :_MAX_TABLE_COLS_TO_MODEL]
        preview = preview_df.to_markdown(index=False)
        return f"{result.answer}\n\nResult table:\n{preview}"

    def create_chart_tool(
        chart_type: str,
        x: str | None = None,
        y: str | None = None,
        title: str = "Analysis",
    ) -> str:
        """Render a chart from the most recent result (or the raw dataset).

        Distribution-style charts (histogram/box/scatter/heatmap) use the raw
        dataset; aggregated charts (bar/line/area/pie/donut) use the table from
        the preceding run_operation call."""
        if not session.has_data:
            return "No dataset is loaded."
        if chart_type not in CHART_TYPES or chart_type == "none":
            return f"Unknown chart_type '{chart_type}'."

        if chart_type in RAW_DATA_CHARTS:
            data = session.df
        else:
            data = session.last_table if not session.last_table.empty else session.df

        path = make_chart(chart_type, data, x, y, title)
        if path is None:
            return (
                f"Could not render a {chart_type} chart with x={x!r}, y={y!r}. "
                "Check that those columns exist in the result table."
            )
        session.set_chart(path)
        return f"Chart created ({chart_type}). It is now shown to the user in the Chart tab."

    return [
        StructuredTool.from_function(
            func=get_schema,
            name="get_schema",
            description="Inspect the loaded dataset: columns, dtypes, null counts and sample values.",
        ),
        StructuredTool.from_function(
            func=run_operation_tool,
            name="run_operation",
            description="Compute an analytical result over the dataset (summary, average, top_n, groupby_agg, correlation, etc.).",
            args_schema=RunOperationArgs,
        ),
        StructuredTool.from_function(
            func=create_chart_tool,
            name="create_chart",
            description="Render a chart (bar, line, pie, histogram, scatter, box, heatmap, ...) from the latest result.",
            args_schema=CreateChartArgs,
        ),
    ]
