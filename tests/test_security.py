"""Tests for the security/robustness hardening."""

from __future__ import annotations

import os

import pandas as pd

import pytest

from data_analyst.core import loader
from data_analyst.core.filters import apply_filters
from data_analyst.core.loader import MAX_SCHEMA_COLUMNS, build_schema, load_dataframe
from data_analyst.core.session import AnalystSession


def test_contains_filter_treats_value_as_literal_not_regex():
    df = pd.DataFrame({"code": ["a.b", "axb", "a+b", "zzz"]})
    # As a regex, "a.b" would match "axb"; as a literal it must not.
    out = apply_filters(df, [{"column": "code", "operator": "contains", "value": "a.b"}])
    assert out["code"].tolist() == ["a.b"]


def test_contains_filter_no_redos_on_pathological_pattern():
    # A catastrophic-backtracking regex must be harmless when treated literally.
    df = pd.DataFrame({"t": ["aaaaaaaaaa!"]})
    out = apply_filters(df, [{"column": "t", "operator": "contains", "value": "(a+)+$"}])
    assert len(out) == 0  # literal "(a+)+$" is not a substring


def test_schema_caps_columns():
    wide = pd.DataFrame({f"c{i}": [1, 2] for i in range(MAX_SCHEMA_COLUMNS + 25)})
    schema = build_schema(wide)
    assert "more columns (not detailed)" in schema
    # Only the capped number of per-column detail lines are emitted.
    detail_lines = [ln for ln in schema.splitlines() if ln.strip().startswith("- c")]
    assert len(detail_lines) == MAX_SCHEMA_COLUMNS


def test_schema_truncates_huge_cell_values():
    df = pd.DataFrame({"big": ["x" * 5000]})
    schema = build_schema(df)
    assert "x" * 5000 not in schema  # the sample value was truncated


def test_row_cap_rejects_oversized_table(tmp_path, monkeypatch):
    monkeypatch.setattr(loader, "MAX_ROWS", 3)
    p = tmp_path / "big.csv"
    pd.DataFrame({"a": range(10)}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="row limit"):
        load_dataframe(str(p))


def test_invalid_xlsx_is_rejected(tmp_path):
    # A non-zip file with an .xlsx extension must not crash the parser.
    p = tmp_path / "fake.xlsx"
    p.write_text("this is not really a workbook")
    with pytest.raises(ValueError, match="valid XLSX"):
        load_dataframe(str(p))


def test_xlsx_zipbomb_guard(tmp_path, monkeypatch):
    # With the uncompressed limit forced to 0, any real workbook is rejected,
    # exercising the zip-bomb guard path.
    monkeypatch.setattr(loader, "MAX_XLSX_UNCOMPRESSED_MB", 0)
    p = tmp_path / "ok.xlsx"
    pd.DataFrame({"a": [1, 2, 3]}).to_excel(p, index=False)
    with pytest.raises(ValueError, match="too large"):
        load_dataframe(str(p))


def test_safe_escapes_html_in_summary():
    from data_analyst.ui.app import _safe

    assert _safe("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_set_chart_deletes_previous_temp_file(tmp_path):
    session = AnalystSession()
    old = tmp_path / "old.png"
    old.write_bytes(b"fake")
    new = tmp_path / "new.png"
    new.write_bytes(b"fake")

    session.set_chart(str(old))
    session.set_chart(str(new))
    assert not old.exists()      # previous chart cleaned up
    assert new.exists()

    session.clear_chart()
    assert not new.exists()      # current chart cleaned up
    assert session.last_chart_path is None
