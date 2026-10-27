
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import src.main as main_module


class TestMainPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.project_dir = Path(self.temp_dir.name)

        self.input_file = self.project_dir / "customers.csv"
        self.processed_file = (
            self.project_dir / "processed" / "customers_cleaned.csv"
        )
        self.report_file = (
            self.project_dir / "outputs" / "validation_report.csv"
        )

    def run_pipeline(self):
        with (
            patch.object(main_module, "INPUT_FILE", self.input_file),
            patch.object(main_module, "PROCESSED_FILE", self.processed_file),
            patch.object(main_module, "REPORT_FILE", self.report_file),
        ):
            main_module.main()

    def write_csv(self, email="alice@example.com"):
        self.input_file.write_text(
            "Customer_ID,Name,Email,City\n"
            f"C001,Alice,{email},Douala\n"
            "C002,Bob,bob@example.com,Yaounde\n",
            encoding="utf-8",
        )

    def test_invalid_data_blocks_export_and_generates_report(self):
        self.write_csv(email="")

        self.run_pipeline()

        self.assertFalse(self.processed_file.exists())
        self.assertTrue(self.report_file.exists())

        report = pd.read_csv(self.report_file)

        self.assertEqual(report.iloc[0]["Status"], "BLOCKED")
        self.assertIn("ERROR", report["Record_Type"].tolist())
        self.assertEqual(report.iloc[0]["Export_Status"], "BLOCKED")

    def test_valid_data_is_exported_successfully(self):
        self.write_csv()

        self.run_pipeline()

        self.assertTrue(self.processed_file.exists())
        self.assertTrue(self.report_file.exists())

        cleaned = pd.read_csv(self.processed_file)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(
            cleaned.loc[0, "Email"],
            "alice@example.com",
        )

        report = pd.read_csv(self.report_file)

        self.assertEqual(report.iloc[0]["Status"], "VALID")
        self.assertEqual(report.iloc[0]["Export_Status"], "SUCCESS")

    def test_invalid_data_removes_stale_export(self):
        self.write_csv()
        self.run_pipeline()

        self.assertTrue(self.processed_file.exists())

        self.write_csv(email="")
        self.run_pipeline()

        self.assertFalse(self.processed_file.exists())

        report = pd.read_csv(self.report_file)

        self.assertEqual(report.iloc[0]["Status"], "BLOCKED")
        self.assertEqual(report.iloc[0]["Export_Status"], "BLOCKED")


    def test_missing_source_file_generates_load_failure_report(self):
        self.processed_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_file.write_text("stale export", encoding="utf-8")

        self.run_pipeline()

        self.assertFalse(self.processed_file.exists())
        self.assertTrue(self.report_file.exists())

        report = pd.read_csv(self.report_file)
        self.assertEqual(report.iloc[0]["Status"], "LOAD_FAILED")
        self.assertEqual(report.iloc[0]["Export_Status"], "BLOCKED")

    def test_empty_source_file_generates_load_failure_report(self):
        self.input_file.write_text("", encoding="utf-8")

        self.run_pipeline()

        self.assertFalse(self.processed_file.exists())
        self.assertTrue(self.report_file.exists())

        report = pd.read_csv(self.report_file)
        self.assertEqual(report.iloc[0]["Status"], "LOAD_FAILED")

    def test_malformed_source_file_generates_load_failure_report(self):
        self.input_file.write_text(
            "Customer_ID,Name\n"
            "C001,Alice\n"
            "C002,Bob,unexpected_value\n",
            encoding="utf-8",
        )

        self.run_pipeline()

        self.assertFalse(self.processed_file.exists())
        self.assertTrue(self.report_file.exists())

        report = pd.read_csv(self.report_file)
        self.assertEqual(report.iloc[0]["Status"], "LOAD_FAILED")
        self.assertEqual(report.iloc[0]["Export_Status"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
