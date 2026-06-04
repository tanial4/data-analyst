import pandas as pd
import pytest

from data_analyst.core.loader import build_schema, load_dataframe


def test_load_csv(tmp_path, sample_df):
    p = tmp_path / "data.csv"
    sample_df.to_csv(p, index=False)
    df = load_dataframe(str(p))
    assert len(df) == len(sample_df)
    assert list(df.columns) == list(sample_df.columns)


def test_load_strips_column_whitespace(tmp_path):
    p = tmp_path / "data.csv"
    pd.DataFrame({" a ": [1], "b": [2]}).to_csv(p, index=False)
    df = load_dataframe(str(p))
    assert "a" in df.columns


def test_load_detects_dates(tmp_path):
    p = tmp_path / "data.csv"
    pd.DataFrame({"d": ["2021-01-01", "2021-02-01", "2021-03-01"]}).to_csv(p, index=False)
    df = load_dataframe(str(p))
    assert str(df["d"].dtype).startswith("datetime64")


def test_load_unsupported_format(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("nope")
    with pytest.raises(ValueError):
        load_dataframe(str(p))


def test_build_schema_lists_column_types(sample_df):
    schema = build_schema(sample_df)
    assert "Rows: 6" in schema
    assert "sales" in schema
    assert "Numeric columns:" in schema
