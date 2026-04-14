import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch

import pandas as pd
import pytest

from src.components.snapshot import compute_snapshot_metrics
from src.utils.metric_snapshots import load_metric_snapshot, save_metric_snapshot


class TestComputeSnapshotMetrics:
    def test_none_df_returns_zero_metrics(self):
        result = compute_snapshot_metrics(None, None)
        assert result["core"]["total_qty"] == 0
        assert result["core"]["total_revenue"] == 0
        assert result["core"]["total_orders"] == 0
        assert result["core"]["avg_basket_value"] == 0

    def test_valid_df_returns_correct_totals(self):
        df = pd.DataFrame(
            {
                "Quantity": [2, 3, 5],
                "Item Cost": [100.0, 200.0, 50.0],
                "Category": ["Shirts", "Shirts", "Pants"],
            }
        )
        basket = {"total_orders": 10, "avg_basket_value": 150.0}
        result = compute_snapshot_metrics(df, basket)

        assert result["core"]["total_qty"] == 10
        # revenue = 2*100 + 3*200 + 5*50 = 200 + 600 + 250 = 1050
        assert result["core"]["total_revenue"] == 1050.0
        assert result["core"]["total_orders"] == 10
        assert result["core"]["avg_basket_value"] == 150.0
        assert result["volume_by_category"]["Shirts"] == 5
        assert result["volume_by_category"]["Pants"] == 5


class TestMetricSnapshotIO:
    def test_save_metric_snapshot_writes_json(self, tmp_path):
        metrics = {"core": {"total_qty": 42}, "timestamp": "2024-01-01T00:00:00"}
        file_path = str(tmp_path / "test_snapshot.json")
        returned_path = save_metric_snapshot(metrics, path=file_path)

        assert returned_path == file_path
        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["core"]["total_qty"] == 42

    def test_load_metric_snapshot_reads_back(self, tmp_path):
        metrics = {"core": {"total_qty": 99}, "timestamp": "2024-06-15T12:00:00"}
        file_path = str(tmp_path / "snapshot_load.json")
        save_metric_snapshot(metrics, path=file_path)

        loaded = load_metric_snapshot(file_path)
        assert loaded is not None
        assert loaded["core"]["total_qty"] == 99

    def test_load_metric_snapshot_returns_none_for_missing_file(self, tmp_path):
        missing = str(tmp_path / "does_not_exist.json")
        assert load_metric_snapshot(missing) is None
