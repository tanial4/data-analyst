import os

from data_analyst.charts.engine import make_chart


def test_bar_chart_returns_path(sample_df):
    agg = sample_df.groupby("region")["sales"].sum().reset_index()
    path = make_chart("bar", agg, "region", "sales", "Sales by region")
    assert path is not None and os.path.exists(path)


def test_histogram_from_raw(sample_df):
    path = make_chart("histogram", sample_df, "sales", None, "Distribution")
    assert path is not None and os.path.exists(path)


def test_heatmap(sample_df):
    path = make_chart("heatmap", sample_df, None, None, "Correlations")
    assert path is not None and os.path.exists(path)


def test_none_chart_returns_none(sample_df):
    assert make_chart("none", sample_df, None, None, "x") is None


def test_missing_columns_returns_none(sample_df):
    # bar needs both x and y to exist; nonexistent columns must not raise
    assert make_chart("bar", sample_df, "nope", "alsonope", "x") is None


def test_unknown_chart_type_returns_none(sample_df):
    assert make_chart("wormhole", sample_df, "region", "sales", "x") is None
