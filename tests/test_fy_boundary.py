"""
FY-boundary staleness gap (2026-06-25): the cancer pipeline now also ingests the
per-MONTH Combined CSVs on the current FY's sub-page, so a new financial year's
data appears immediately instead of trailing until NHS posts the cumulative file.

The per-month file is column-for-column identical to the cumulative EXCEPT it
omits the `Period` column (the month is implicit in the filename). These tests pin:
  * discovery classifies cumulative vs per-month and parses the per-month month;
  * normalise injects the month from the filename when Period is absent, and
    cross-checks it when Period IS present;
  * the REQUIRED fail-loud month-label guard fires on a bad filename parse;
  * the contiguity guard fires on a missing month;
  * merge precedence: final>provisional, then cumulative>per-month at equal status.
"""
import pandas as pd
import pytest

from pipeline import discover, normalise


# --- discovery: shape + month classification --------------------------------

def _anchor(href, text):
    return f'<a href="{href}">{text}</a>'


def test_discover_classifies_cumulative_and_permonth():
    html = "".join([
        _anchor("https://x/2025-26-Apr-Sep-Cumulative-Monthly-Combined-CSV-Final.csv",
                "2025-26 Apr – Sep Monthly Combined CSV Final"),
        _anchor("https://x/April-2026-Monthly-Combined-CSV-Provisional.csv",
                "April 2026 Monthly Combined CSV Provisional"),
    ])
    items = {i["url"].rsplit("/", 1)[-1]: i for i in discover.discover_csv_links(html)}
    cumul = items["2025-26-Apr-Sep-Cumulative-Monthly-Combined-CSV-Final.csv"]
    assert cumul["shape"] == "cumulative" and cumul["month"] is None
    assert cumul["financial_year"] == "2025-26" and cumul["status"] == "final"
    perm = items["April-2026-Monthly-Combined-CSV-Provisional.csv"]
    assert perm["shape"] == "monthly" and perm["month"] == "2026-04"
    assert perm["financial_year"] == "2026-27" and perm["status"] == "provisional"


def test_current_financial_year():
    import datetime as dt
    assert discover.current_financial_year(dt.date(2026, 4, 1)) == "2026-27"
    assert discover.current_financial_year(dt.date(2026, 3, 31)) == "2025-26"
    assert discover.fy_subpage_url("2026-27").endswith(
        "/2026-27-monthly-cancer-waiting-times-statistics/")


def test_unparseable_monthly_filename_flagged_for_refusal():
    # A Combined CSV that is neither FY-prefixed nor cleanly month-prefixed is
    # treated as monthly-with-unknown-month so run.py refuses it (never guesses).
    html = _anchor("https://x/Aprl-2026-Monthly-Combined-CSV-Provisional.csv",
                   "Aprl 2026 Monthly Combined CSV Provisional")
    item = discover.discover_csv_links(html)[0]
    assert item["shape"] == "monthly" and item["month"] is None


# --- normalise: month injection + cross-check -------------------------------

def _permonth_row(**over):
    """The per-month layout: NO Period column."""
    row = {
        "Basis": "Provider", "Org_Code": "RXX", "Org_Name": "Test Trust",
        "Standard_or_Item": "62D", "Cancer_Type": "ALL CANCERS",
        "Referral_Route_or_Stage": "ALL ROUTES", "Treatment_Modality": "ALL MODALITIES",
        "Within": 80, "Total": 100,
    }
    row.update(over)
    return row


def test_permonth_injects_month_from_hint():
    df = pd.DataFrame([_permonth_row()])
    out = normalise.normalise(df, "April-2026-Monthly-Combined-CSV-Provisional.csv",
                              "provisional", period_hint="2026-04")
    assert set(out["month"].unique()) == {"2026-04"}


def test_permonth_without_hint_fails_loud():
    df = pd.DataFrame([_permonth_row()])
    with pytest.raises(ValueError, match="no Period/month column"):
        normalise.normalise(df, "April-2026-Monthly-Combined-CSV-Provisional.csv",
                            "provisional", period_hint=None)


def test_period_column_disagreeing_with_hint_fails_loud():
    # A per-month file that unexpectedly carries a Period column whose month
    # contradicts its filename is mislabelled -> stop the build.
    df = pd.DataFrame([_permonth_row(Period="01/05/2026")])
    with pytest.raises(ValueError, match="disagree with the filename month"):
        normalise.normalise(df, "April-2026-Monthly-Combined-CSV-Provisional.csv",
                            "provisional", period_hint="2026-04")


# --- the REQUIRED fail-loud month-label guard -------------------------------

def test_assert_month_label_rejects_bad_parse():
    out = pd.DataFrame({"month": ["2026-04"]})
    with pytest.raises(ValueError, match="did not parse as"):
        normalise.assert_month_label(out, None, "bad.csv")
    with pytest.raises(ValueError, match="did not parse as"):
        normalise.assert_month_label(out, "2026-13", "bad.csv")


def test_assert_month_label_rejects_multi_month_on_permonth_path():
    out = pd.DataFrame({"month": ["2026-04", "2026-05"]})
    with pytest.raises(ValueError, match="single-month file"):
        normalise.assert_month_label(out, "2026-04", "April-2026.csv")


def test_assert_month_label_accepts_clean_single_month():
    out = pd.DataFrame({"month": ["2026-04", "2026-04"]})
    normalise.assert_month_label(out, "2026-04", "April-2026.csv")  # no raise


# --- the contiguity (no duplicate/missing month) guard ----------------------

def _nat(month):
    return {"month": month, "org_level": "national", "org_code": "ENG",
            "org_name": "England", "region": "England", "standard": "CMB62",
            "breakdown_type": "all", "breakdown_value": "All", "within_target": 80,
            "total": 100, "performance": 0.8, "data_status": "final", "source_file": "x"}


def test_contiguity_guard_passes_on_contiguous_series():
    store = pd.DataFrame([_nat("2026-02"), _nat("2026-03"), _nat("2026-04")])
    normalise.assert_contiguous_national_months(store)  # no raise


def test_contiguity_guard_fails_on_missing_month():
    store = pd.DataFrame([_nat("2026-02"), _nat("2026-04")])  # March missing
    with pytest.raises(AssertionError, match="not contiguous"):
        normalise.assert_contiguous_national_months(store)


# --- merge precedence -------------------------------------------------------

def _row(month, status, source_file, within=80):
    return {"month": month, "org_level": "provider", "org_code": "RXX",
            "org_name": "T", "region": "", "standard": "CMB62",
            "breakdown_type": "all", "breakdown_value": "All", "within_target": within,
            "total": 100, "performance": within / 100, "data_status": status,
            "source_file": source_file}


def test_final_beats_provisional_regardless_of_source():
    # per-month FINAL must override a cumulative PROVISIONAL for the same month (a).
    existing = pd.DataFrame([_row("2026-04", "provisional",
                                  "2026-27-Apr-Sep-Cumulative-Monthly-Combined-CSV-Provisional.csv", within=70)])
    new = pd.DataFrame([_row("2026-04", "final",
                             "April-2026-Monthly-Combined-CSV-Final.csv", within=90)])
    merged = normalise.merge_with_revisions(existing, new)
    assert len(merged) == 1 and merged.iloc[0]["within_target"] == 90


def test_cumulative_wins_at_equal_status():
    # equal status (both final) -> cumulative wins over per-month (b), regardless
    # of which was processed first.
    permonth = pd.DataFrame([_row("2026-04", "final",
                                  "April-2026-Monthly-Combined-CSV-Final.csv", within=70)])
    cumul = pd.DataFrame([_row("2026-04", "final",
                               "2026-27-Apr-Sep-Cumulative-Monthly-Combined-CSV-Final.csv", within=90)])
    # cumulative arriving as `new`
    m1 = normalise.merge_with_revisions(permonth, cumul)
    assert m1.iloc[0]["within_target"] == 90
    # cumulative already in the store, per-month arriving as `new` -> still cumulative
    m2 = normalise.merge_with_revisions(cumul, permonth)
    assert m2.iloc[0]["within_target"] == 90
