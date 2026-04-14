import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from src.utils.display import truncate_label


class TestTruncateLabel:
    def test_short_string_returned_as_is(self):
        assert truncate_label("Hello") == "Hello"

    def test_exact_max_len_string_returned_as_is(self):
        text = "a" * 25
        assert truncate_label(text) == text

    def test_long_string_truncated_with_ellipsis(self):
        text = "a" * 30
        result = truncate_label(text)
        assert len(result) == 25
        assert result.endswith("...")

    def test_empty_string_returned_as_is(self):
        assert truncate_label("") == ""

    def test_custom_max_len_works(self):
        text = "Hello World"
        result = truncate_label(text, max_len=8)
        assert result == "Hello..."
        assert len(result) == 8
