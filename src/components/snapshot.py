"""JSON metric snapshot — replaces the old PNG html2canvas screenshot."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import streamlit as st

from src.utils.metric_snapshots import save_metric_snapshot


def compute_snapshot_metrics(
    granular_df: pd.DataFrame | None,
    basket_metrics: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compute a snapshot of core metrics from the current dashboard state.

    Args:
        granular_df: The granular (row-level) DataFrame currently displayed.
        basket_metrics: Pre-computed basket metrics dict from ``aggregate_data``.

    Returns:
        Dict with keys: timestamp, core, volume_by_category, revenue_by_category.
    """
    tz_bd = timezone(timedelta(hours=6))
    snapshot: dict[str, Any] = {
        "timestamp": datetime.now(tz_bd).isoformat(),
        "core": {
            "total_qty": 0,
            "total_revenue": 0,
            "total_orders": 0,
            "avg_basket_value": 0,
        },
        "volume_by_category": {},
        "revenue_by_category": {},
    }

    if granular_df is None or granular_df.empty:
        return snapshot

    # Core metrics
    qty = granular_df["Quantity"].sum() if "Quantity" in granular_df.columns else 0
    revenue = (
        (granular_df["Quantity"] * granular_df["Item Cost"]).sum()
        if {"Quantity", "Item Cost"}.issubset(granular_df.columns)
        else 0
    )

    snapshot["core"]["total_qty"] = int(qty)
    snapshot["core"]["total_revenue"] = float(revenue)

    if basket_metrics:
        snapshot["core"]["total_orders"] = int(basket_metrics.get("total_orders", 0))
        snapshot["core"]["avg_basket_value"] = round(
            float(basket_metrics.get("avg_basket_value", 0)), 2
        )

    # Category breakdowns
    if "Category" in granular_df.columns:
        vol = granular_df.groupby("Category")["Quantity"].sum()
        snapshot["volume_by_category"] = {k: int(v) for k, v in vol.items()}

        if "Item Cost" in granular_df.columns:
            rev = granular_df.copy()
            rev["_rev"] = rev["Quantity"] * rev["Item Cost"]
            rev_by_cat = rev.groupby("Category")["_rev"].sum()
            snapshot["revenue_by_category"] = {
                k: round(float(v), 2) for k, v in rev_by_cat.items()
            }

    return snapshot


def render_snapshot_button(
    granular_df: pd.DataFrame | None = None,
    basket_metrics: dict[str, Any] | None = None,
) -> None:
    """Render a download button for a JSON metric snapshot.

    If no data is available, shows a disabled-looking info message instead.

    Args:
        granular_df: Row-level DataFrame for metric computation.
        basket_metrics: Pre-computed basket metrics dict.
    """
    metrics = compute_snapshot_metrics(granular_df, basket_metrics)

    json_str = json.dumps(metrics, indent=2, default=str)

    col_left, col_right = st.columns([4, 1])
    with col_right:
        st.download_button(
            label="Save Snapshot",
            data=json_str,
            file_name=f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )
