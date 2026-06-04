import pytest

from data_analyst.core.operations import run_operation


def test_average(sample_df):
    res = run_operation(sample_df, "average", target_column="sales")
    # mean of [100,200,150,50,300,250] = 175
    assert "175" in res.answer
    assert res.table.loc[0, "Value"] == pytest.approx(175.0)


def test_sum(sample_df):
    res = run_operation(sample_df, "sum", target_column="sales")
    assert res.table.loc[0, "Value"] == pytest.approx(1050.0)


def test_top_n(sample_df):
    res = run_operation(sample_df, "top_n", target_column="sales", top_n=2)
    assert len(res.table) == 2
    assert res.table["sales"].tolist() == [300, 250]


def test_top_n_ascending(sample_df):
    res = run_operation(sample_df, "top_n", target_column="sales", top_n=1, sort_order="asc")
    assert res.table["sales"].tolist() == [50]


def test_groupby_agg_sum(sample_df):
    res = run_operation(sample_df, "groupby_agg", target_column="sales", groupby_column="region", agg_func="sum")
    assert "sum_sales" in res.table.columns
    west = res.table.loc[res.table["region"] == "West", "sum_sales"].iloc[0]
    assert west == pytest.approx(550.0)  # 100 + 150 + 300


def test_groupby_count(sample_df):
    res = run_operation(sample_df, "groupby_agg", groupby_column="region", agg_func="count")
    assert "count" in res.table.columns


def test_correlation_matrix(sample_df):
    res = run_operation(sample_df, "correlation")
    # sales and units are perfectly correlated by construction
    assert "Correlation" in res.answer or "correlation" in res.answer.lower()


def test_list_unique(sample_df):
    res = run_operation(sample_df, "list_unique", target_column="region")
    assert "3 unique" in res.answer


def test_full_stats(sample_df):
    res = run_operation(sample_df, "full_stats", target_column="sales")
    assert "Statistic" in res.table.columns


def test_summary(sample_df):
    res = run_operation(sample_df, "summary")
    assert "rows" in res.answer.lower()


def test_unknown_operation(sample_df):
    res = run_operation(sample_df, "frobnicate")
    assert "not recognized" in res.answer


def test_filters_applied_before_op(sample_df):
    res = run_operation(
        sample_df, "sum", target_column="sales",
        filters=[{"column": "region", "operator": "==", "value": "East"}],
    )
    assert res.table.loc[0, "Value"] == pytest.approx(250.0)  # 200 + 50


def test_empty_after_filter(sample_df):
    res = run_operation(
        sample_df, "sum", target_column="sales",
        filters=[{"column": "region", "operator": "==", "value": "Nowhere"}],
    )
    assert "No rows match" in res.answer
