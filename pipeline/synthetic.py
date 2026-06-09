"""
Synthetic CWT data generator.

Produces a CSV that mimics the *structure* of NHS England's Monthly Combined
CSV (post-Nov-2025 style column names from COLUMN_CANDIDATES), so the whole
pipeline can be developed and tested without network access to england.nhs.uk.

The NUMBERS ARE FABRICATED and must never be presented as real. They are shaped
to be plausible (e.g. 62-day performance drifting in the 60-75% range) only so
charts look realistic during development.
"""
import numpy as np
import pandas as pd

# A small, realistic set of providers (real ODS codes + names) and ICBs.
PROVIDERS = [
    ("RJ1", "Guy's and St Thomas' NHS Foundation Trust"),
    ("R0A", "Manchester University NHS Foundation Trust"),
    ("RGT", "Cambridge University Hospitals NHS Foundation Trust"),
    ("RA7", "University Hospitals Bristol and Weston NHS FT"),
    ("RTH", "Oxford University Hospitals NHS Foundation Trust"),
    ("RR8", "Leeds Teaching Hospitals NHS Trust"),
]
ICBS = [
    ("QHM", "NHS North Central London ICB"),
    ("QOP", "NHS Greater Manchester ICB"),
    ("QUE", "NHS Cambridgeshire and Peterborough ICB"),
]

STANDARD_LABELS = {
    "FDS28": "28-day FDS",
    "CMB31": "31-day combined",
    "CMB62": "62-day combined",
}
# Rough baseline performance per standard, with the 62-day the worst.
BASELINE = {"FDS28": 0.78, "CMB31": 0.91, "CMB62": 0.67}

CANCER_TYPES = ["All", "Breast", "Lower GI", "Lung", "Skin", "Urological"]


def _series_for(code, base, n_months, rng):
    """A noisy, slightly trending monthly performance series in [0,1]."""
    trend = np.linspace(0, rng.uniform(-0.04, 0.04), n_months)
    noise = rng.normal(0, 0.02, n_months)
    org_offset = rng.uniform(-0.08, 0.08)
    vals = np.clip(base + org_offset + trend + noise, 0.4, 0.99)
    return vals


def generate(start="2023-10", n_months=18, seed=42):
    rng = np.random.default_rng(seed)
    months = pd.period_range(start=start, periods=n_months, freq="M").strftime("%Y-%m")
    rows = []

    orgs = ([("ENG", "England", "national")]
            + [(c, n, "provider") for c, n in PROVIDERS]
            + [(c, n, "icb") for c, n in ICBS])

    for code, name, level in orgs:
        for std_code, std_label in STANDARD_LABELS.items():
            perf = _series_for(std_code, BASELINE[std_code], n_months, rng)
            base_total = {"national": 30000, "provider": 1200, "icb": 4000}[level]
            for i, month in enumerate(months):
                # 'All' breakdown row
                total = int(base_total * rng.uniform(0.85, 1.15))
                within = int(total * perf[i])
                rows.append([month, std_label, level.upper(), code, name,
                             "all", "All", within, total])
                # add a cancer-type breakdown for the two combined standards
                if std_code in ("CMB31", "CMB62") and level == "provider":
                    for ct in CANCER_TYPES[1:]:
                        t = int(total / 6 * rng.uniform(0.5, 1.5))
                        if t <= 0:
                            continue
                        p = np.clip(perf[i] + rng.normal(0, 0.04), 0.4, 0.99)
                        rows.append([month, std_label, level.upper(), code, name,
                                     "cancer", ct, int(t * p), t])

    df = pd.DataFrame(rows, columns=[
        "MONTH", "STANDARD", "ORG_LEVEL", "ORG_CODE", "ORG_NAME",
        "BREAKDOWN", "BREAKDOWN_VALUE", "WITHIN_STANDARD", "TOTAL",
    ])
    return df


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "data/raw/synthetic_combined.csv"
    generate().to_csv(out, index=False)
    print(f"wrote {out}")
