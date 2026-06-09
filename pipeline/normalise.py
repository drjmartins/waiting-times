"""
Normalisation: NHS source CSV -> canonical tidy schema.

The combined CSV is long-thin, but its layout has changed more than once. The
Nov-2025 format change was STRUCTURAL, not just renamed headers: the breakdown
is no longer a single (type, value) pair but is spread across three columns
(cancer type, referral route/stage, treatment modality), there is no explicit
org level (rows are Provider/Commissioner 'basis', with the all-England total
shipping as a pseudo-org 'Total'), and the period is DD/MM/YYYY.

We therefore:
  * map a set of *candidate* source column names onto each scalar canonical
    field (add new candidates here, in one place, when headers change);
  * DERIVE breakdown_type/value from the three-column layout when present,
    RETAINING every breakdown row (the site build narrows to 'all'; the by-
    cancer / by-modality rows are kept as raw material for later views);
  * derive org_level from basis + the 'Total' pseudo-org.

If a required scalar field can't be mapped, we raise a clear error naming the
file and the missing field, so a format change fails loudly in the pipeline
(and in CI) rather than silently producing wrong numbers.
"""
import pandas as pd

from . import config

# Candidate source-column names for each required scalar field. Add to these
# lists when NHS changes the layout; order = priority.
COLUMN_CANDIDATES = {
    "month":           ["MONTH", "PERIOD", "Period", "Month", "REPORTING_PERIOD"],
    "org_level":       ["ORG_LEVEL", "LEVEL", "ORG TYPE", "ORG_TYPE", "Basis"],
    "org_code":        ["ORG_CODE", "ORG CODE", "CODE", "PROVIDER_CODE", "ICB_CODE", "Org_Code"],
    "org_name":        ["ORG_NAME", "ORG NAME", "NAME", "PROVIDER_NAME", "ICB_NAME", "Org_Name"],
    "standard":        ["STANDARD", "MEASURE", "CWT_STANDARD", "Standard_or_Item"],
    "within_target":   ["WITHIN_STANDARD", "WITHIN_TARGET", "TREATED_WITHIN", "SEEN_WITHIN_STANDARD", "Within"],
    "total":           ["TOTAL", "TOTAL_TREATED", "TOTAL_SEEN", "DENOMINATOR", "Total"],
}

# Breakdown handling supports two source shapes:
#   (a) an explicit, pre-collapsed (type, value) pair -- the synthetic generator
#       and any future source that ships breakdown columns directly; or
#   (b) NHS England's post-Nov-2025 three-column layout, derived below.
BREAKDOWN_TYPE_CANDIDATES = ["BREAKDOWN", "BREAKDOWN_TYPE", "CATEGORY_TYPE"]
BREAKDOWN_VALUE_CANDIDATES = ["BREAKDOWN_VALUE", "CATEGORY", "STAGE", "CANCER_TYPE", "MODALITY", "ROUTE"]

# NHS three-column breakdown layout: canonical dimension -> source column.
REAL_BREAKDOWN_COLS = {
    "cancer":   "Cancer_Type",
    "route":    "Referral_Route_or_Stage",
    "modality": "Treatment_Modality",
}

# Per-dimension values that mean "not broken down on this dimension" (i.e. the
# aggregate). NaN/blank also counts as aggregate (e.g. FDS carries no modality).
_ALL_MARKERS = {
    "cancer":   {"all cancers"},
    "route":    {"all routes", "all stages"},
    "modality": {"all modalities"},
}

# Map NHS standard labels (as they appear in the source) to our internal codes.
# Matched as case-insensitive substrings, so both the verbose pre-2025 labels
# and the terse post-2025 codes ('FDS', '31D', '62D') resolve. Anything not
# listed (e.g. the USC / breast-symptomatic referral items) maps to None and is
# dropped.
STANDARD_LABEL_MAP = {
    "28-day fds": "FDS28", "faster diagnosis": "FDS28", "fds": "FDS28",
    "31-day combined": "CMB31", "31 day combined": "CMB31", "31d": "CMB31",
    "62-day combined": "CMB62", "62 day combined": "CMB62", "62d": "CMB62",
}


def _find_column(df, candidates):
    for cand in candidates:
        if cand in df.columns:
            return cand
    return None


def _map_standard(value):
    v = str(value).strip().lower()
    for key, code in STANDARD_LABEL_MAP.items():
        if key in v:
            return code
    return None


def _is_aggregate(series, dim):
    low = series.astype(str).str.strip().str.lower()
    return low.isin(_ALL_MARKERS[dim]) | low.isin(["nan", ""])


def _derive_breakdown(df):
    """
    Collapse NHS's three breakdown columns into (breakdown_type, breakdown_value)
    per row, keeping EVERY row. A dimension is 'aggregate' if its value is an
    ALL-marker or blank. Classify by how many dimensions are actually broken
    down:
        0  -> ('all', 'All')                       (the headline figure)
        1  -> (<that dimension>, <its value>)       e.g. ('cancer', 'Breast')
       >1  -> ('combination', 'a | b')              non-aggregate parts joined
    """
    dims = list(REAL_BREAKDOWN_COLS)
    raw = {dim: df[col].astype(str).str.strip() for dim, col in REAL_BREAKDOWN_COLS.items()}
    nonagg = pd.DataFrame({dim: ~_is_aggregate(df[REAL_BREAKDOWN_COLS[dim]], dim) for dim in dims})
    counts = nonagg.sum(axis=1)

    btype = pd.Series("combination", index=df.index)
    bvalue = pd.Series("", index=df.index)

    btype[counts == 0] = "all"
    bvalue[counts == 0] = "All"

    for dim in dims:
        mask = (counts == 1) & nonagg[dim]
        btype[mask] = dim
        bvalue[mask] = raw[dim][mask]

    combo_mask = counts >= 2
    if combo_mask.any():
        def _combo_row(r):
            parts = [str(r[col]).strip() for dim, col in REAL_BREAKDOWN_COLS.items()
                     if str(r[col]).strip().lower() not in _ALL_MARKERS[dim]
                     and str(r[col]).strip().lower() not in ("nan", "")]
            return " | ".join(parts)
        bvalue.loc[combo_mask] = df.loc[combo_mask].apply(_combo_row, axis=1)

    return btype, bvalue


def normalise(df, source_file, data_status):
    """Take a raw source DataFrame, return a DataFrame in CANONICAL_COLUMNS."""
    rename = {}
    for field, candidates in COLUMN_CANDIDATES.items():
        col = _find_column(df, candidates)
        if col is None:
            raise ValueError(
                f"{source_file}: could not map required field '{field}'. "
                f"Add its source column name to COLUMN_CANDIDATES. "
                f"Columns present: {list(df.columns)[:30]}"
            )
        rename[col] = field
    out = df.rename(columns=rename)

    # Breakdown: prefer an explicit (type, value) pair; else derive from the NHS
    # three-column layout. Either way, every row is retained.
    bt_col = _find_column(out, BREAKDOWN_TYPE_CANDIDATES)
    bv_col = _find_column(out, BREAKDOWN_VALUE_CANDIDATES)
    if bt_col and bv_col:
        out["breakdown_type"] = out[bt_col].astype(str).str.strip().str.lower()
        out["breakdown_value"] = out[bv_col]
    elif all(c in df.columns for c in REAL_BREAKDOWN_COLS.values()):
        bt, bv = _derive_breakdown(df)
        out["breakdown_type"] = bt.values
        out["breakdown_value"] = bv.values
    else:
        raise ValueError(
            f"{source_file}: could not determine breakdown columns. Expected either "
            f"a type/value pair {BREAKDOWN_TYPE_CANDIDATES}/{BREAKDOWN_VALUE_CANDIDATES} "
            f"or the NHS three-column layout {list(REAL_BREAKDOWN_COLS.values())}. "
            f"Columns present: {list(df.columns)[:30]}"
        )

    out["standard"] = out["standard"].map(_map_standard)
    out = out[out["standard"].notna()]  # drop USC/breast-symptomatic referral rows

    # Coerce numerics; bad rows -> NaN then dropped.
    out["within_target"] = pd.to_numeric(out["within_target"], errors="coerce")
    out["total"] = pd.to_numeric(out["total"], errors="coerce")
    out = out[(out["total"].notna()) & (out["total"] > 0)]

    # Org level. Source ships a Provider/Commissioner 'basis' (or an explicit
    # level in the synthetic file); the all-England aggregate arrives as a
    # pseudo-org 'Total'. Normalise to our national/provider/icb vocabulary.
    out["org_level"] = out["org_level"].astype(str).str.strip().str.lower()
    out["org_level"] = out["org_level"].replace({"commissioner": "icb"})
    is_national = out["org_code"].astype(str).str.strip().str.lower() == "total"
    out.loc[is_national, "org_level"] = "national"
    out.loc[is_national, "org_code"] = "ENG"
    out.loc[is_national, "org_name"] = "England"

    out["performance"] = (out["within_target"] / out["total"]).round(4)
    out["data_status"] = data_status
    out["source_file"] = source_file

    # Normalise month to YYYY-MM. File vintages differ: older files use ISO
    # (YYYY-MM-DD), the 2025-26 files use DD/MM/YYYY. Parse ISO first, then fall
    # back to day-first for whatever didn't match -- a blanket dayfirst=True
    # would misread ISO dates as year-day-month and collapse every month to one.
    parsed = pd.to_datetime(out["month"], errors="coerce", format="%Y-%m-%d")
    fallback = parsed.isna()
    if fallback.any():
        parsed = parsed.copy()
        parsed[fallback] = pd.to_datetime(out["month"][fallback], errors="coerce", dayfirst=True)
    out["month"] = parsed.dt.strftime("%Y-%m")
    out = out[out["month"].notna()]

    return out[config.CANONICAL_COLUMNS].reset_index(drop=True)


def merge_with_revisions(existing, new):
    """
    Combine existing tidy data with a newly-processed file, applying the
    revisions rule: for any (month, org_code, standard, breakdown_value) key,
    the newest data wins, and 'final' always beats 'provisional'.
    """
    if existing is None or len(existing) == 0:
        return new
    combined = pd.concat([existing, new], ignore_index=True)
    # final (1) sorts after provisional (0); keep last per key.
    combined["_rank"] = (combined["data_status"] == "final").astype(int)
    combined = combined.sort_values("_rank")
    key = ["month", "org_level", "org_code", "standard", "breakdown_type", "breakdown_value"]
    combined = combined.drop_duplicates(subset=key, keep="last")
    return combined.drop(columns="_rank").reset_index(drop=True)
