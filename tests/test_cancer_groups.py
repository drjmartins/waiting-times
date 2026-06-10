"""
Tests for the NHS ten-group cancer aggregation (pipeline/cancer_groups.py and
the cancer_group dimension in build_site_data._breakdown_payload).

Guards, in order of importance:
  1. EXHAUSTIVENESS: every Cancer_Type value in the real tidy store maps to a
     group (a new NHS label must fail loudly, not silently vanish).
  2. SUMMING not averaging: a group's performance is numerators/denominators
     summed across its constituent types, then divided — never the mean of the
     per-type percentages.
  3. RECONCILIATION: the ten groups' summed denominators equal the all-cancers
     total per (month, org, standard) in the real store, across ALL THREE
     standards. This is the gate that lets the shared filter exist.
  4. DOUBLE-COUNT guard: a parent label and its children must not co-occur.
"""
import os

import pandas as pd
import pytest

from pipeline import cancer_groups as cg
from pipeline import build_site_data as b

STORE = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "tidy.parquet")
_HAS_STORE = os.path.exists(STORE)
_store_only = pytest.mark.skipif(not _HAS_STORE, reason="real tidy store not present")


def test_ten_groups_are_canonical():
    assert cg.TEN_GROUPS == (
        "Breast", "Gynaecology", "Haematology", "Head & Neck", "Lower GI",
        "Lung", "Other", "Skin", "Upper GI", "Urology")
    assert set(cg.GROUP_OF.values()) == set(cg.TEN_GROUPS)  # every group is reachable


def test_group_for_known_and_hierarchy():
    assert cg.group_for("Breast") == "Breast"
    assert cg.group_for("Haematological - Lymphoma") == "Haematology"
    assert cg.group_for("Acute leukaemia") == "Haematology"          # rare cancer -> Haem
    assert cg.group_for("Testicular") == "Urology"                   # rare cancer -> Urology
    assert cg.group_for("Urological - Prostate") == "Urology"
    assert cg.group_for("Upper Gastrointestinal - Hepatobiliary") == "Upper GI"
    # FDS28 sites with no dashboard group fall to the catch-all
    assert cg.group_for("Suspected brain/central nervous system tumours") == "Other"
    assert cg.group_for("Suspected sarcoma") == "Other"
    assert cg.group_for("Missing or Invalid") == "Other"
    assert cg.group_for("  Breast  ") == "Breast"                    # whitespace-tolerant


def test_group_for_raises_on_unknown():
    with pytest.raises(cg.UnmappedCancerType):
        cg.group_for("Suspected toe cancer")


def test_assert_no_double_count_flags_parent_plus_child():
    # parent + its children in one cell would double the denominator
    with pytest.raises(ValueError):
        cg.assert_no_double_count(["Haematological", "Haematological - Lymphoma"])
    # parent-only or children-only is fine (the real-data pattern)
    cg.assert_no_double_count(["Haematological"])
    cg.assert_no_double_count(["Haematological - Lymphoma", "Haematological - Other (a)"])


def _crow(month, group_value, within, total, std="CMB62", status="final"):
    return {
        "month": month, "org_level": "provider", "org_code": "RAA",
        "org_name": "RAA Trust", "region": "London", "standard": std,
        "breakdown_type": "cancer", "breakdown_value": group_value,
        "within_target": within, "total": total,
        "performance": round(within / total, 4), "data_status": status,
        "source_file": "t.csv",
    }


def test_group_sums_numerators_not_averages_percentages():
    # Two Haematology constituents in one month: 9/10 (90%) and 1/990 (~0.1%).
    # Mean-of-% = 45%. Volume-weighted (correct) = 10/1000 = 1.0%. Must not conflate.
    rows = pd.DataFrame([
        _crow("2025-07", "Haematological - Lymphoma", 9, 10),
        _crow("2025-07", "Haematological - Other (a)", 1, 990),
    ])
    pay = b._breakdown_payload(rows)
    haem = pay["standards"]["CMB62"]["cancer_group"]["Haematology"]
    assert haem["within_target"] == [10] and haem["total"] == [1000]   # summed
    assert haem["performance"] == [round(10 / 1000, 4)]                 # pooled, not 0.45


def test_group_omitted_when_no_constituents():
    rows = pd.DataFrame([_crow("2025-07", "Lung", 5, 8)])
    groups = b._breakdown_payload(rows)["standards"]["CMB62"]["cancer_group"]
    assert set(groups) == {"Lung"}            # only groups with data appear


@_store_only
def test_real_store_every_label_maps():
    df = pd.read_parquet(STORE)
    labels = df.loc[df["breakdown_type"] == "cancer", "breakdown_value"]
    mapped = cg.assert_all_mapped(labels)     # raises if any unmapped
    assert len(mapped) >= 16                   # CMB31 has 16; FDS/CMB62 add more


@_store_only
def test_real_store_reconciles_across_all_three_standards():
    df = pd.read_parquet(STORE)
    can = df[df["breakdown_type"] == "cancer"].copy()
    can["group"] = can["breakdown_value"].map(cg.group_for)
    g = can.groupby(["month", "org_code", "standard"], as_index=False).agg(
        g_total=("total", "sum"), g_within=("within_target", "sum"))
    a = (df[df["breakdown_type"] == "all"]
         .groupby(["month", "org_code", "standard"], as_index=False)
         .agg(a_total=("total", "sum"), a_within=("within_target", "sum")))
    m = g.merge(a, on=["month", "org_code", "standard"], how="outer", indicator=True)
    # every cell with a headline has cancer rows and vice versa
    assert (m["_merge"] == "both").all(), m["_merge"].value_counts().to_dict()
    # denominators (and numerators) reconcile within NHS rounding slack (<1 patient)
    for std in ("FDS28", "CMB31", "CMB62"):
        s = m[m["standard"] == std]
        assert (s["g_total"] - s["a_total"]).abs().max() < 0.6, std
        assert (s["g_within"] - s["a_within"]).abs().max() < 0.6, std


@_store_only
def test_real_store_all_ten_groups_present_in_each_standard():
    df = pd.read_parquet(STORE)
    can = df[df["breakdown_type"] == "cancer"].copy()
    can["group"] = can["breakdown_value"].map(cg.group_for)
    for std in ("FDS28", "CMB31", "CMB62"):
        present = set(can.loc[can["standard"] == std, "group"])
        assert present == set(cg.TEN_GROUPS), (std, set(cg.TEN_GROUPS) - present)
