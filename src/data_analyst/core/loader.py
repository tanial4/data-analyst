"""Loading tabular files into DataFrames and describing them as text schemas."""

from __future__ import annotations

import pandas as pd
from pandas.api import types as ptypes


def load_dataframe(file_path: str) -> pd.DataFrame:
    """Read a CSV/XLSX/XLS file into a cleaned DataFrame.

    - Falls back to latin-1 for CSVs that are not valid UTF-8.
    - Drops duplicate columns and strips whitespace from column names.
    - Heuristically converts object columns to datetime when most values parse
      as dates (>= 60% of a 20-row sample).

    Raises ``ValueError`` for unsupported formats or empty files.
    """
    path_lower = file_path.lower()
    if path_lower.endswith(".csv"):
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")
    elif path_lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported format. Please upload CSV, XLSX, or XLS.")

    if df.empty:
        raise ValueError("The uploaded file is empty.")

    df = df.loc[:, ~df.columns.duplicated()].copy()
    df.columns = [str(c).strip() for c in df.columns]

    for col in df.columns:
        # Text columns are 'object' in pandas 2.x and a dedicated 'str' dtype in
        # pandas 3.x; treat both as candidates for date parsing.
        if ptypes.is_numeric_dtype(df[col]) or ptypes.is_datetime64_any_dtype(df[col]):
            continue
        sample = df[col].dropna().astype(str).head(20)
        if len(sample) > 0:
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            if parsed.notna().mean() >= 0.6:
                df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
    return df


def build_schema(df: pd.DataFrame) -> str:
    """Render a human/LLM-readable description of a DataFrame's structure."""
    lines = [f"Rows: {len(df)}", f"Columns: {len(df.columns)}", "Schema:"]
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = int(df[col].notna().sum())
        nulls = int(df[col].isna().sum())
        sample = df[col].dropna().astype(str).head(5).tolist()
        lines.append(
            f"  - {col} | type={dtype} | non_null={non_null} | nulls={nulls} | sample={sample}"
        )
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "string", "category", "bool"]).columns.tolist()
    dt_cols = df.select_dtypes(include="datetime").columns.tolist()
    lines += [
        f"Numeric columns: {num_cols}",
        f"Categorical columns: {cat_cols}",
        f"Date columns: {dt_cols}",
    ]
    return "\n".join(lines)
