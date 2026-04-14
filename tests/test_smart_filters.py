import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import pytest

from src.components.smart_filters import detect_filterable_columns


class TestDetectFilterableColumns:
    def test_empty_dataframe_returns_empty_dict(self):
        df = pd.DataFrame()
        assert detect_filterable_columns(df) == {}

    def test_datetime_column_detected_as_date(self):
        df = pd.DataFrame(
            {"order_date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"])}
        )
        result = detect_filterable_columns(df)
        assert result.get("order_date") == "date"

    def test_numeric_column_detected_as_numeric(self):
        df = pd.DataFrame({"price": [10.5, 20.0, 30.0, 40.0, 50.0]})
        result = detect_filterable_columns(df)
        assert result.get("price") == "numeric"

    def test_categorical_column_detected(self):
        """Low-cardinality object column should be detected as categorical."""
        df = pd.DataFrame(
            {"status": ["Active", "Inactive", "Active", "Pending"] * 10}
        )
        result = detect_filterable_columns(df)
        assert result.get("status") == "categorical"

    def test_high_cardinality_string_column_not_detected(self):
        """A column with many unique values (likely IDs) should not be detected."""
        df = pd.DataFrame({"record_name": [f"rec_{i}" for i in range(200)]})
        result = detect_filterable_columns(df)
        assert "record_name" not in result

    def test_column_with_phone_in_name_is_skipped(self):
        df = pd.DataFrame({"phone_number": ["017xxx", "018xxx", "019xxx"] * 5})
        result = detect_filterable_columns(df)
        assert "phone_number" not in result
