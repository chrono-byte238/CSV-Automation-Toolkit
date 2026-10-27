
from pathlib import Path

import pandas as pd

from src.cleaner import clean_dataframe
from src.validator import validate_dataframe
from src.report import (
    generate_report,
    generate_load_error_report,
)


PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "raw" / "customers.csv"
PROCESSED_FILE = (
    PROJECT_DIR / "data" / "processed" / "customers_cleaned.csv"
)
REPORT_FILE = PROJECT_DIR / "outputs" / "validation_report.csv"


def main():
    print("=== CSV AUTOMATION TOOLKIT ===")

    # 1. Load the source file.
    try:
        df = pd.read_csv(INPUT_FILE, skipinitialspace=True)

    except (
        FileNotFoundError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as error:
        print(f"Unable to load the source file: {error}")

        # Remove output from a previous successful run.
        if PROCESSED_FILE.exists():
            PROCESSED_FILE.unlink()
            print("Removed stale processed output.")

        # Record the failure of the current run.
        generate_load_error_report(
            error_message=str(error),
            output_path=REPORT_FILE,
        )

        print(f"Report generated: {REPORT_FILE}")
        return

    print(f"Original rows: {len(df)}")

    # 2. Clean a copy of the source data.
    cleaned_df = clean_dataframe(df)

    # 3. Validate the cleaned data.
    result = validate_dataframe(cleaned_df)

    print(f"Cleaned rows: {len(cleaned_df)}")
    print(f"Blocking errors: {len(result['errors'])}")
    print(f"Warnings: {len(result['warnings'])}")

    # 4. Export only when validation succeeds.
    if result["is_valid"]:
        PROCESSED_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cleaned_df.to_csv(
            PROCESSED_FILE,
            index=False,
            encoding="utf-8-sig",
        )

        export_status = "SUCCESS"
        print(f"Cleaned file exported to: {PROCESSED_FILE}")

    else:
        export_status = "BLOCKED"

        # Remove a stale generated export, if one exists.
        if PROCESSED_FILE.exists():
            PROCESSED_FILE.unlink()
            print("Removed stale processed output.")

        print("Export blocked. Fix the errors before processing.")

        for validation_error in result["errors"]:
            print(f"ERROR: {validation_error}")

    # 5. Generate a report after successful loading.
    generate_report(
        validation_result=result,
        original_rows=len(df),
        cleaned_rows=len(cleaned_df),
        output_path=REPORT_FILE,
        export_status=export_status,
    )

    print(f"Report generated: {REPORT_FILE}")


if __name__ == "__main__":
    main()
