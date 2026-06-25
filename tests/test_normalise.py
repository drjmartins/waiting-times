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


def test_region_captured_from_parent_org():
    out = _normalise([_real_row("01/10/2025", Parent_Org="North West")])
    assert out["region"].iloc[0] == "North West"


def test_region_absent_is_blank_not_error():
    # synthetic / future sources without a region column must not break
    out = _normalise([_real_row("01/10/2025")])
    assert out["region"].iloc[0] == ""


# --- the pandas-3.0 blank-dimension guard (silent-failure-prone) -------------
# FDS rows carry NO modality dimension, so Treatment_Modality is BLANK/NaN. The
# breakdown derivation must treat a blank dimension as AGGREGATE. pandas 3.0
# changed astype(str) to preserve NaN (no longer "nan"), which silently broke the
# old string-based aggregate check and mis-classified every blank-modality FDS
# row as a real breakdown — FDS28's headline 'all' slice vanished from the build.
# The existing fixtures never caught it because they set Treatment_Modality
# explicitly to "ALL MODALITIES". These pin the blank/NaN case directly.

def test_blank_modality_string_is_aggregate():
    """A blank (empty-string) modality on an FDS all-cancers row -> 'all' slice."""
    out = _normalise([_real_row("01/10/2025", Standard_or_Item="FDS", Treatment_Modality="")])
    assert out["breakdown_type"].iloc[0] == "all"
    assert out["breakdown_value"].iloc[0] == "All"


def test_nan_modality_is_aggregate_fds_cancer_row():
    """A genuine NaN modality (as pandas reads an empty CSV cell) must be treated
    as aggregate: an FDS by-cancer row classifies to 'cancer', NOT 'combination'."""
    import numpy as np
    out = _normalise([_real_row("01/10/2025", Standard_or_Item="FDS",
                                Cancer_Type="Suspected breast cancer",
                                Treatment_Modality=np.nan)])
    assert out["breakdown_type"].iloc[0] == "cancer"
    assert out["breakdown_value"].iloc[0] == "Suspected breast cancer"


def test_is_aggregate_helper_catches_nan_directly():
    import numpy as np
    s = pd.Series(["ALL MODALITIES", "", np.nan, "Surgery"])
    agg = normalise._is_aggregate(s, "modality")
    assert agg.tolist() == [True, True, True, False]
