
import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean column names and text fields, then remove exact duplicates."""

    cleaned_df = df.copy()

    initial_rows = len(cleaned_df)

    # 1. Normalize column names.
    cleaned_df.columns = cleaned_df.columns.str.strip()

    # 2. Remove unnecessary surrounding spaces from text fields.
    text_columns = cleaned_df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        cleaned_df[column] = cleaned_df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    # Treat empty strings as missing values.
    cleaned_df = cleaned_df.replace(r"^\s*$", pd.NA, regex=True)

    # 3. Count missing values before removing duplicate rows.
    missing_values = {
        column: int(count)
        for column, count in cleaned_df.isna().sum().items()
        if count > 0
    }

    # 4. Remove exact duplicate rows.
    duplicate_count = int(cleaned_df.duplicated().sum())
    cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)

    report = {
        "initial_rows": initial_rows,
        "final_rows": len(cleaned_df),
        "duplicates_removed": duplicate_count,
        "missing_values_by_column": missing_values,
    }

    return cleaned_df
