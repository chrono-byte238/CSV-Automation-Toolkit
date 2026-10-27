
from pathlib import Path

import pandas as pd


REPORT_COLUMNS = [
    "Record_Type",
    "Status",
    "Message",
    "Original_Rows",
    "Cleaned_Rows",
    "Duplicates_Removed",
    "Export_Status",
]


def generate_report(
    validation_result: dict,
    original_rows: int,
    cleaned_rows: int,
    output_path: Path,
    export_status: str,
) -> None:
    """Generate a fresh CSV report for the latest processing run."""

    errors = validation_result["errors"]
    warnings = validation_result["warnings"]

    records = [
        {
            "Record_Type": "SUMMARY",
            "Status": (
                "VALID"
                if validation_result["is_valid"]
                else "BLOCKED"
            ),
            "Message": (
                "Validation successful."
                if validation_result["is_valid"]
                else "The file contains blocking errors."
            ),
            "Original_Rows": int(original_rows),
            "Cleaned_Rows": int(cleaned_rows),
            "Duplicates_Removed": int(original_rows - cleaned_rows),
            "Export_Status": export_status,
        }
    ]

    for error in errors:
        records.append({
            "Record_Type": "ERROR",
            "Status": "BLOCKING",
            "Message": error,
            "Original_Rows": "",
            "Cleaned_Rows": "",
            "Duplicates_Removed": "",
            "Export_Status": export_status,
        })

    for warning in warnings:
        records.append({
            "Record_Type": "WARNING",
            "Status": "NOTICE",
            "Message": warning,
            "Original_Rows": "",
            "Cleaned_Rows": "",
            "Duplicates_Removed": "",
            "Export_Status": export_status,
        })

    report_df = pd.DataFrame(records, columns=REPORT_COLUMNS)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

def generate_load_error_report(
    error_message: str,
    output_path: Path,
) -> None:
    """Generate a report when the source file cannot be loaded."""

    records = [
        {
            "Record_Type": "SUMMARY",
            "Status": "LOAD_FAILED",
            "Message": "The source file could not be loaded.",
            "Original_Rows": 0,
            "Cleaned_Rows": 0,
            "Duplicates_Removed": 0,
            "Export_Status": "BLOCKED",
        },
        {
            "Record_Type": "ERROR",
            "Status": "LOAD_FAILED",
            "Message": error_message,
            "Original_Rows": "",
            "Cleaned_Rows": "",
            "Duplicates_Removed": "",
            "Export_Status": "BLOCKED",
        },
    ]

    report_df = pd.DataFrame(records, columns=REPORT_COLUMNS)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )
