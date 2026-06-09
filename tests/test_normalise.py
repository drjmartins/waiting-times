"""
Regression tests for normalise.py.

The headline guard here is the DATE FORMAT one. NHS mixes date formats across
file vintages -- ISO YYYY-MM-DD in the older files, DD/MM/YYYY in the 2025-26
files. A blanket dayfirst=True parses the new files but silently misreads the
ISO dates as year-day-month, collapsing every month in the older files to
January. That failure is silent (no error, just wrong numbers), so it must be
pinned by a test: if a future NHS file reintroduces the mixing, CI fails loudly.
"""
import pandas as pd

from pipeline import normalise


def _real_row(period, **over):
    """A minimal row in the post-Nov-2025 NHS Combined-CSV layout (62D, all-slice)."""
    row = {
        "Period": period,
        "Basis": "Provider",
        "Org_Code": "RXX",
        "Org_Name": "Test Trust",
        "Standard_or_Item": "62D",
        "Cancer_Type": "ALL CANCERS",
        "Referral_Route_or_Stage": "ALL ROUTES",
        "Treatment_Modality": "ALL MODALITIES",
        "Within": 80,
        "Total": 100,
    }
    row.update(over)
    return row


def _normalise(rows):
    return normalise.normalise(pd.DataFrame(rows), "test.csv", "final")


# --- the date-format guard ---------------------------------------------------

def test_iso_dates_parse_to_correct_month():
    """Older-vintage ISO dates (YYYY-MM-DD) must keep their real month."""
    out = _normalise([_real_row("2023-05-01"), _real_row("2024-02-01")])
    assert sorted(out["month"]) == ["2023-05", "2024-02"]


def test_dayfirst_dates_parse_to_correct_month():
    """2025-26-vintage DD/MM/YYYY dates must parse day-first, not month-first."""
    out = _normalise([_real_row("01/10/2025"), _real_row("01/03/2026")])
    assert sorted(out["month"]) == ["2025-10", "2026-03"]


def test_mixed_vintages_in_one_frame_both_correct():
    """Both formats together: the regression that shipped 16/48 months mangled."""
    out = _normalise([_real_row("2023-05-01"), _real_row("01/10/2025")])
    assert sorted(out["month"]) == ["2023-05", "2025-10"]
    # the specific bug: ISO May must NOT collapse to January
    assert "2023-01" not in set(out["month"])


# --- closely-related structural guards (also silent-failure-prone) -----------

def test_total_pseudo_org_becomes_national():
    out = _normalise([_real_row("01/10/2025", Org_Code="Total", Org_Name="Total")])
    assert out["org_level"].iloc[0] == "national"
    assert out["org_code"].iloc[0] == "ENG"


def test_commissioner_basis_maps_to_icb():
    out = _normalise([_real_row("01/10/2025", Basis="Commissioner", Org_Code="QT1")])
    assert out["org_level"].iloc[0] == "icb"


def test_all_slice_is_detected():
    out = _normalise([_real_row("01/10/2025")])
    assert out["breakdown_type"].iloc[0] == "all"
    assert out["breakdown_value"].iloc[0] == "All"
