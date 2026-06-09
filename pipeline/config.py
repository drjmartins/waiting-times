"""
Configuration for the Cancer Waiting Times data pipeline.

Single source of truth for: where the data lives, the standards we track,
and the canonical schema we normalise every source file into.
"""

# NHS England publishes the combined CSVs (one per financial year) on this page.
# The pipeline scrapes it for links rather than hard-coding file URLs, because
# the URLs embed upload dates that change every release.
SOURCE_PAGE = "https://www.england.nhs.uk/statistics/statistical-work-areas/cancer-waiting-times/"

# We only want the "Monthly Combined CSV" links (provider + commissioner in one
# table). These substrings identify them in the page's anchor text.
COMBINED_CSV_MARKERS = ("Monthly Combined CSV",)

# The October 2023 standards change means 31-day and 62-day figures before this
# month are NOT comparable to those after. The dashboard defaults to this start
# date and treats earlier data as a separate, clearly-labelled historic series.
COMPARABILITY_BREAK = "2023-10"

# The three headline standards plus the two "referral seen" measures, keyed by a
# short internal code. `target` is the operational standard (proportion) used as
# the default in the size-of-the-prize calculator; None where no % target applies.
STANDARDS = {
    "FDS28":  {"label": "28-day Faster Diagnosis Standard", "target": 0.75, "unit_days": 28},
    "CMB31":  {"label": "31-day combined (decision-to-treat to treatment)", "target": 0.96, "unit_days": 31},
    "CMB62":  {"label": "62-day combined (referral to treatment)", "target": 0.85, "unit_days": 62},
}

# Canonical tidy schema. Every source row, whatever its original layout, is
# normalised to exactly these columns. One row = one month x org x standard x
# breakdown-slice.
CANONICAL_COLUMNS = [
    "month",          # YYYY-MM (period the activity relates to)
    "org_level",      # 'national' | 'provider' | 'icb'
    "org_code",       # ODS code, e.g. 'RJ1'; 'ENG' for national
    "org_name",       # human-readable
    "region",         # NHS England region (from Parent_Org); 'England' if region-less
    "standard",       # one of STANDARDS keys
    "breakdown_type", # 'all' | 'cancer' | 'modality' | 'route'
    "breakdown_value",# e.g. 'All', 'Breast', 'Surgery', 'Screening'
    "within_target",  # count seen within the standard
    "total",          # denominator: total in scope
    "performance",    # within_target / total (0-1), computed
    "data_status",    # 'provisional' | 'final'
    "source_file",    # provenance: which CSV this row came from
]

# --- Trust comparison view (see comparison-view-spec.md) --------------------
# THE reliability threshold (single source of truth): a trust-period aggregate
# with a denominator below this is "sub-threshold" -- shown in the funnel only,
# never the percentile view.
RELIABILITY_THRESHOLD = 10

# Comparison basis: the most recent N FINALISED months, pooled by summing
# numerators and denominators (never averaging monthly percentages).
COMPARISON_WINDOW_MONTHS = 3

# Funnel control limits, anchored to the national distribution. z for two-sided
# 95% (~2 SD) and 99.8% (~3 SD), per standard funnel methodology.
FUNNEL_LIMITS = {"p95": 1.96, "p998": 3.09}

# Region scopes available as comparison comparators (England is implicit).
NHS_REGIONS = [
    "East of England", "London", "Midlands", "North East and Yorkshire",
    "North West", "South East", "South West",
]

# A region needs at least this many threshold-clearing trusts for a measure,
# else the scope widens one step (region -> England).
REGION_MIN_TRUSTS = 5

# Breakdown dimensions a user can narrow a measure by (combination rows are kept
# in the store but are not offered as comparison measures in v1).
COMPARISON_BREAKDOWNS = ["all", "cancer", "route", "modality"]

# Where things get written.
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
SITE_DATA_DIR = "site/data"
MANIFEST_PATH = "data/manifest.json"
