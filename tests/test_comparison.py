"""
Tests for the comparison precompute (build_site_data).

The methods-critical guard is the AGGREGATION rule: pool the recent finalised
window by summing numerators and denominators, never by averaging monthly
percentages (which mis-weights months of different sizes). Also guards the
finalised-only period selection, the sub-threshold flag, and FY bucketing.
"""
import json
import os

import pandas as pd

from pipeline import build_site_data as b
from pipeline import config


def test_financial_year():
    assert b._financial_year("2025-07") == "2025-26"
    assert b._financial_year("2025-03") == "2024-25"
    assert b._financial_year("2025-04") == "2025-26"


def test_recent_final_months_excludes_provisional():
    df = pd.DataFrame({
        "month": ["2025-05", "2025-06", "2025-07", "2025-08", "2025-09"],
        "data_status": ["final", "final", "final", "provisional", "provisional"],
    })
    # window is 3; provisional months must be excluded even though they're newer
    assert b._recent_final_months(df) == ["2025-05", "2025-06", "2025-07"]


def _row(month, code, within, total, status="final", std="CMB62"):
    return {
        "month": month, "org_level": "provider", "org_code": code,
        "org_name": code + " Trust", "region": "London", "standard": std,
        "breakdown_type": "all", "breakdown_value": "All",
        "within_target": within, "total": total,
        "performance": round(within / total, 4), "data_status": status,
        "source_file": "t.csv",
    }


def test_pooling_sums_numerators_not_averages_percentages(tmp_path):
    # Trust A: month1 90/100 (90%), month2 10/100 (10%). Mean-of-% = 50%.
    # Correct pooled = (90+10)/(100+100) = 50%. Make them DIFFER to catch it:
    # month1 90/100 (90%), month2 5/900 (~0.56%). Mean-of-% = 45.3%, but the
    # volume-weighted pooled = 95/1000 = 9.5%. They must not be conflated.
    df = pd.DataFrame([
        _row("2025-07", "RAA", 90, 100),
        _row("2025-08", "RAA", 5, 900),
        _row("2025-09", "RAA", 50, 1000),
    ])
    b._build_comparison(df, str(tmp_path))
    d = json.load(open(tmp_path / "compare" / "CMB62__all__All.json"))
    t = d["trusts"][0]
    assert t["within"] == 145 and t["total"] == 2000      # summed, not averaged
    assert t["performance"] == round(145 / 2000, 4)        # 0.0725, pooled
    assert d["national"]["performance"] == round(145 / 2000, 4)


def test_sub_threshold_flag(tmp_path):
    df = pd.DataFrame([
        _row("2025-07", "BIG", 80, 100),
        _row("2025-07", "TINY", 4, 6),   # total 6 < threshold 10
    ])
    b._build_comparison(df, str(tmp_path))
    d = json.load(open(tmp_path / "compare" / "CMB62__all__All.json"))
    flags = {t["code"]: t["sub_threshold"] for t in d["trusts"]}
    assert flags["TINY"] is True and flags["BIG"] is False
    assert d["threshold"] == config.RELIABILITY_THRESHOLD
