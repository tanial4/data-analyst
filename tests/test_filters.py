from data_analyst.core.filters import apply_filters


def test_equality_filter(sample_df):
    out = apply_filters(sample_df, [{"column": "region", "operator": "==", "value": "West"}])
    assert set(out["region"]) == {"West"}
    assert len(out) == 3


def test_numeric_filter(sample_df):
    out = apply_filters(sample_df, [{"column": "sales", "operator": ">", "value": 150}])
    assert (out["sales"] > 150).all()


def test_contains_filter(sample_df):
    out = apply_filters(sample_df, [{"column": "product", "operator": "contains", "value": "a"}])
    # case-insensitive: matches product "A"
    assert len(out) == 3


def test_unknown_column_is_skipped(sample_df):
    out = apply_filters(sample_df, [{"column": "missing", "operator": "==", "value": 1}])
    assert len(out) == len(sample_df)


def test_none_filters(sample_df):
    assert len(apply_filters(sample_df, None)) == len(sample_df)
