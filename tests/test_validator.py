
import unittest

import pandas as pd

from src.validator import validate_dataframe


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.valid_df = pd.DataFrame({
            "Customer_ID": ["C001"],
            "Name": ["Alice"],
            "Email": ["alice@example.com"],
            "City": ["Douala"],
        })

    def test_accepts_valid_data(self):
        result = validate_dataframe(self.valid_df)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["warnings"], [])

    def test_missing_email_blocks_validation(self):
        df = self.valid_df.copy()
        df.loc[0, "Email"] = pd.NA

        result = validate_dataframe(df)

        self.assertFalse(result["is_valid"])
        self.assertTrue(
            any("Email is missing" in error
                for error in result["errors"])
        )

    def test_invalid_email_blocks_validation(self):
        df = self.valid_df.copy()
        df.loc[0, "Email"] = "alice@"

        result = validate_dataframe(df)

        self.assertFalse(result["is_valid"])
        self.assertTrue(
            any("Invalid email format" in error
                for error in result["errors"])
        )

    def test_missing_city_is_a_warning(self):
        df = self.valid_df.copy()
        df.loc[0, "City"] = pd.NA

        result = validate_dataframe(df)

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["errors"], [])
        self.assertTrue(
            any("City is missing" in warning
                for warning in result["warnings"])
        )

    def test_missing_required_column_blocks_validation(self):
        df = self.valid_df.drop(columns=["Email"])

        result = validate_dataframe(df)

        self.assertFalse(result["is_valid"])
        self.assertTrue(
            any("Missing required columns" in error
                for error in result["errors"])
        )


if __name__ == "__main__":
    unittest.main()
