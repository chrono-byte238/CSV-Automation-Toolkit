
import unittest

import pandas as pd

from src.cleaner import clean_dataframe


class TestCleaner(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            " Customer_ID ": ["C001", "C002", "C002"],
            " Name ": [" Alice ", " Bob ", " Bob "],
            "Email": [
                "alice@example.com",
                "bob@example.com",
                "bob@example.com",
            ],
            "City": ["Douala", "Yaounde", "Yaounde"],
        })

    def test_removes_exact_duplicates(self):
        cleaned = clean_dataframe(self.df)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned.duplicated().sum(), 0)
    def test_converts_blank_strings_to_missing_values(self):
        df = self.df.copy()
        df.loc[0, "Email"] = "   "

        cleaned = clean_dataframe(df)

        self.assertTrue(pd.isna(cleaned.loc[0, "Email"]))
    def test_strips_column_names(self):
        cleaned = clean_dataframe(self.df)

        self.assertEqual(
            list(cleaned.columns),
            ["Customer_ID", "Name", "Email", "City"],
        )

    def test_strips_text_spaces(self):
        cleaned = clean_dataframe(self.df)

        self.assertEqual(cleaned.iloc[0]["Name"], "Alice")

    def test_preserves_original_dataframe(self):
        original = self.df.copy(deep=True)

        clean_dataframe(self.df)

        pd.testing.assert_frame_equal(self.df, original)


if __name__ == "__main__":
    unittest.main()
