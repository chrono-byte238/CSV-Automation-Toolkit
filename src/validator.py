
import pandas as pd
import re


REQUIRED_COLUMNS = ["Customer_ID", "Name", "Email", "City"]

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_dataframe(df: pd.DataFrame) -> dict:
    """
    Validate a DataFrame without modifying its contents.

    Missing or malformed emails block the file.
    Missing customer IDs or names also block the file.
    Missing cities generate warnings.
    """

    errors = []
    warnings = []

    # Normalize column names for checking only.
    column_lookup = {
        str(column).strip(): column
        for column in df.columns
    }

    # Check required columns.
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in column_lookup
    ]

    if missing_columns:
        errors.append(
            f"Missing required columns: {missing_columns}"
        )

        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    # Check customer IDs and names.
    for column in ["Customer_ID", "Name"]:
        values = (
            df[column_lookup[column]]
            .astype("string")
            .str.strip()
        )

        missing_mask = values.isna() | values.eq("").fillna(False)

        for position in range(len(df)):
            if missing_mask.iloc[position]:
                errors.append(
                    f"Row {position + 2}: "
                    f"{column} is missing."
                )

    # Check email addresses.
    emails = (
        df[column_lookup["Email"]]
        .astype("string")
        .str.strip()
    )

    missing_email = (
        emails.isna() | emails.eq("").fillna(False)
    )

    for position in range(len(df)):
        if missing_email.iloc[position]:
            errors.append(
                f"Row {position + 2}: Email is missing."
            )
        elif not EMAIL_PATTERN.fullmatch(emails.iloc[position]):
            errors.append(
                f"Row {position + 2}: "
                f"Invalid email format: {emails.iloc[position]}"
            )

    # Missing cities are warnings, not blocking errors.
    cities = (
        df[column_lookup["City"]]
        .astype("string")
        .str.strip()
    )

    missing_city = (
        cities.isna() | cities.eq("").fillna(False)
    )

    for position in range(len(df)):
        if missing_city.iloc[position]:
            warnings.append(
                f"Row {position + 2}: City is missing."
            )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
