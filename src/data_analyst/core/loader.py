"""Loading tabular files into DataFrames and describing them as text schemas."""

from __future__ import annotations

import zipfile

import pandas as pd
from pandas.api import types as ptypes

#: An XLSX is a zip archive; a small upload can decompress to gigabytes in
#: memory (a "zip bomb"). Reject workbooks whose *uncompressed* size exceeds this.
MAX_XLSX_UNCOMPRESSED_MB = 300

#: Hard cap on rows after loading — a backstop against memory/CPU exhaustion from
#: a file that is small on disk but expands into an enormous table.
MAX_ROWS = 2_000_000


def _check_xlsx_not_zipbomb(file_path: str) -> None:
    """Raise ``ValueError`` if an XLSX decompresses beyond the allowed size."""
    try:
        with zipfile.ZipFile(file_path) as zf:
            uncompressed = sum(info.file_size for info in zf.infolist())
    except zipfile.BadZipFile:
        raise ValueError("This file is not a valid XLSX workbook.")
    if uncompressed > MAX_XLSX_UNCOMPRESSED_MB * 1024 * 1024:
        raise ValueError("This workbook is too large to process safely.")


def load_dataframe(file_path: str) -> pd.DataFrame:
    """Read a CSV/XLSX file into a cleaned DataFrame.

    - Falls back to latin-1 for CSVs that are not valid UTF-8.
    - Rejects XLSX zip bombs and over-large tables.
    - Drops duplicate columns and strips whitespace from column names.
    - Heuristically converts object columns to datetime when most values parse
      as dates (>= 60% of a 20-row sample).

    Raises ``ValueError`` for unsupported formats, empty/oversized files.
    """
    path_lower = file_path.lower()
    if path_lower.endswith(".csv"):
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")
    elif path_lower.endswith(".xlsx"):
        _check_xlsx_not_zipbomb(file_path)
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError("Unsupported format. Please upload a CSV or XLSX file.")

    if df.empty:
        raise ValueError("The uploaded file is empty.")
    if len(df) > MAX_ROWS:
        raise ValueError(
            f"This dataset has {len(df):,} rows, above the {MAX_ROWS:,}-row limit. "
            "Please upload a sample."
        )

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


#: Cap how many columns are described per-column in the schema. The schema is
#: sent to the LLM on every turn, so an unbounded list (a pathologically wide
#: file) would blow up token usage and cost. Detail the first N; summarize the rest.
MAX_SCHEMA_COLUMNS = 60

#: Truncate long sample values so a single huge cell can't bloat the prompt.
_MAX_SAMPLE_CHARS = 60


def build_schema(df: pd.DataFrame) -> str:
    """Render a human/LLM-readable description of a DataFrame's structure."""
    lines = [f"Rows: {len(df)}", f"Columns: {len(df.columns)}", "Schema:"]
    for col in df.columns[:MAX_SCHEMA_COLUMNS]:
        dtype = str(df[col].dtype)
        non_null = int(df[col].notna().sum())
        nulls = int(df[col].isna().sum())
        sample = [s[:_MAX_SAMPLE_CHARS] for s in df[col].dropna().astype(str).head(5).tolist()]
        lines.append(
            f"  - {col} | type={dtype} | non_null={non_null} | nulls={nulls} | sample={sample}"
        )
    if len(df.columns) > MAX_SCHEMA_COLUMNS:
        lines.append(f"  ... and {len(df.columns) - MAX_SCHEMA_COLUMNS} more columns (not detailed).")
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "string", "category", "bool"]).columns.tolist()
    dt_cols = df.select_dtypes(include="datetime").columns.tolist()
    lines += [
        f"Numeric columns: {num_cols}",
        f"Categorical columns: {cat_cols}",
        f"Date columns: {dt_cols}",
    ]
    return "\n".join(lines)
