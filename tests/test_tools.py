"""Tests for the agent tools that don't require an LLM (the deterministic path)."""

import os

from data_analyst.agent.tools import build_tools
from data_analyst.core.session import AnalystSession


def _session(sample_df):
    s = AnalystSession()
    s.load(sample_df, "sample.csv")
    return s


def _tools_by_name(session):
    return {t.name: t for t in build_tools(session)}


def test_get_schema_tool(sample_df):
    tools = _tools_by_name(_session(sample_df))
    out = tools["get_schema"].invoke({})
    assert "sales" in out


def test_run_operation_tool_stores_table(sample_df):
    session = _session(sample_df)
    tools = _tools_by_name(session)
    out = tools["run_operation"].invoke({"operation": "sum", "target_column": "sales"})
    assert "1,050" in out or "1050" in out
    assert not session.last_table.empty


def test_run_operation_tool_parses_filters(sample_df):
    session = _session(sample_df)
    tools = _tools_by_name(session)
    out = tools["run_operation"].invoke(
        {
            "operation": "sum",
            "target_column": "sales",
            "filters_json": '[{"column":"region","operator":"==","value":"East"}]',
        }
    )
    assert "250" in out


def test_create_chart_tool_sets_path(sample_df):
    session = _session(sample_df)
    tools = _tools_by_name(session)
    tools["run_operation"].invoke(
        {"operation": "groupby_agg", "target_column": "sales", "groupby_column": "region", "agg_func": "sum"}
    )
    out = tools["create_chart"].invoke({"chart_type": "bar", "x": "region", "y": "sum_sales", "title": "By region"})
    assert "Chart created" in out
    assert session.last_chart_path and os.path.exists(session.last_chart_path)


def test_tools_handle_no_data():
    tools = _tools_by_name(AnalystSession())
    assert "No dataset" in tools["run_operation"].invoke({"operation": "summary"})
