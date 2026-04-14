import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch

import pandas as pd
import pytest

from src.utils.safe_ops import safe_column_access, safe_filter, safe_render


class TestSafeFilter:
    @patch("src.utils.safe_ops.st")
    def test_returns_filtered_df_on_success(self, mock_st):
        df = pd.DataFrame({"a": [1, 2, 3, 4]})
        result = safe_filter(df, lambda d: d[d["a"] > 2], "test")
        assert len(result) == 2
        assert list(result["a"]) == [3, 4]
        mock_st.warning.assert_not_called()

    @patch("src.utils.safe_ops.st")
    def test_returns_original_df_when_filter_returns_empty(self, mock_st):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = safe_filter(df, lambda d: d[d["a"] > 100], "empty_filter")
        assert len(result) == 3
        mock_st.warning.assert_called_once()

    @patch("src.utils.safe_ops.st")
    def test_returns_original_df_when_filter_raises_exception(self, mock_st):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = safe_filter(df, lambda d: d["nonexistent_col"], "bad_filter")
        assert len(result) == 3
        mock_st.warning.assert_called_once()


class TestSafeColumnAccess:
    @patch("src.utils.safe_ops.st")
    def test_returns_column_when_exists(self, mock_st):
        df = pd.DataFrame({"x": [10, 20, 30]})
        series = safe_column_access(df, "x")
        assert list(series) == [10, 20, 30]
        mock_st.warning.assert_not_called()

    @patch("src.utils.safe_ops.st")
    def test_returns_default_series_when_column_missing(self, mock_st):
        df = pd.DataFrame({"x": [10, 20, 30]})
        series = safe_column_access(df, "missing_col", default=0)
        assert list(series) == [0, 0, 0]
        assert series.name == "missing_col"
        mock_st.warning.assert_called_once()


class TestSafeRender:
    @patch("src.utils.safe_ops.st")
    def test_returns_value_on_success(self, mock_st):
        result = safe_render(lambda: 42)
        assert result == 42
        mock_st.warning.assert_not_called()

    @patch("src.utils.safe_ops.st")
    def test_returns_none_on_exception(self, mock_st):
        result = safe_render(lambda: 1 / 0, fallback_msg="Oops")
        assert result is None
        mock_st.warning.assert_called_once()
