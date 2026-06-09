"""
Export step: tidy DataFrame -> artefacts the static site consumes.

Outputs:
  site/data/index.json          - list of orgs (for the search/picker)
  site/data/org/<CODE>.json     - per-org time series for all standards
  site/data/national.json       - England series (used as comparison line)
  site/data/compare/index.json  - catalogue of comparison measures
  site/data/compare/<measure>.json - per-measure trust comparison (funnel data)
  site/data/downloads/          - targeted CSV slices + gzipped full file
  site/data/meta.json           - build metadata + comparability note
"""
import gzip
import json
import os
import re
import datetime as dt

import pandas as pd

from . import config

# Non-real placeholder orgs (e.g. the 'UNKNOWN' unallocated-commissioner bucket).
# Hidden from the picker and comparison view, but RETAINED in the tidy store and
# in national totals so sums still reconcile.
PLACEHOLDER_NAMES = {"UNKNOWN"}


def _is_placeholder(code, name):
    return (str(code).strip().upper() in PLACEHOLDER_NAMES
            or str(name).strip().upper() in PLACEHOLDER_NAMES)


def _org_payload(df_org):
    """Build the per-org JSON: one block per standard, 'All' breakdown only."""
    out = {"standards": {}}
    allrows = df_org[df_org["breakdown_type"] == "all"]
    for std in config.STANDARDS:
        s = allrows[allrows["standard"] == std].sort_values("month")
        if len(s) == 0:
            continue
        out["standards"][std] = {
            "label": config.STANDARDS[std]["label"],
            "target": config.STANDARDS[std]["target"],
            "months": s["month"].tolist(),
            "performance": s["performance"].tolist(),
            "within_target": s["within_target"].astype(int).tolist(),
            "total": s["total"].astype(int).tolist(),
            "data_status": s["data_status"].tolist(),
        }
    return out


_MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _financial_year(month):
    """'2025-07' -> '2025-26' (NHS financial year, Apr-Mar)."""
    y, m = (int(x) for x in month.split("-"))
    start = y if m >= 4 else y - 1
    return f"{start}-{str(start + 1)[-2:]}"


def _recent_final_months(df, k=config.COMPARISON_WINDOW_MONTHS):
    """The k most recent FINALISED months (provisional months excluded)."""
    fin = sorted(df.loc[df["data_status"] == "final", "month"].unique())
    return fin[-k:]


def _period_label(months):
    if not months:
        return ""
    a, b = months[0].split("-"), months[-1].split("-")
    am, bm = _MONTH_ABBR[int(a[1]) - 1], _MONTH_ABBR[int(b[1]) - 1]
    if len(months) == 1:
        return f"{am} {a[0]}, finalised"
    if a[0] == b[0]:
        return f"{am}–{bm} {b[0]}, finalised"
    return f"{am} {a[0]}–{bm} {b[0]}, finalised"


def _slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-").lower() or "na"


def _measure_label(std, breakdown_type, breakdown_value):
    base = config.STANDARDS[std]["label"].split("(")[0].strip()
    return f"{base} — all cancers" if breakdown_type == "all" else f"{base} — {breakdown_value}"


def _build_comparison(df, out_dir):
    """
    Precompute one funnel/comparison dataset per measure (standard x optional
    cancer/route/modality), pooled over the recent finalised window by summing
    numerators and denominators. Control-limit anchoring (national p0, z-values,
    threshold) ships in each file; the front end draws the limit curves and does
    scope filtering / fallback. Region scoping is a client filter on the trust
    list, so a single national-anchored file serves every scope.
    """
    months = _recent_final_months(df)
    compare_dir = os.path.join(out_dir, "compare")
    os.makedirs(compare_dir, exist_ok=True)

    prov = df[(df["org_level"] == "provider")
              & (df["month"].isin(months))
              & (df["breakdown_type"].isin(config.COMPARISON_BREAKDOWNS))]
    prov = prov[~prov["org_name"].str.upper().isin(PLACEHOLDER_NAMES)
                & ~prov["org_code"].str.upper().isin(PLACEHOLDER_NAMES)]

    measures, used = [], set()
    for (std, bt, bv), g in prov.groupby(["standard", "breakdown_type", "breakdown_value"]):
        t = g.groupby(["org_code", "org_name", "region"], as_index=False).agg(
            within=("within_target", "sum"), total=("total", "sum"))
        t = t[t["total"] > 0]
        if t.empty:
            continue
        t["performance"] = (t["within"] / t["total"]).round(4)
        t["sub_threshold"] = t["total"] < config.RELIABILITY_THRESHOLD
        within_sum, total_sum = int(t["within"].sum()), int(t["total"].sum())
        p0 = round(within_sum / total_sum, 4) if total_sum else None

        fname = f"{std}__{bt}__{_slug(bv)}.json"
        n = 2
        while fname in used:  # guarantee unique filenames across breakdown values
            fname = f"{std}__{bt}__{_slug(bv)}-{n}.json"
            n += 1
        used.add(fname)

        trusts = [{"code": r.org_code, "name": r.org_name, "region": r.region,
                   "within": int(r.within), "total": int(r.total),
                   "performance": r.performance, "sub_threshold": bool(r.sub_threshold)}
                  for r in t.sort_values("total", ascending=False).itertuples()]
        with open(os.path.join(compare_dir, fname), "w") as f:
            json.dump({
                "standard": std, "breakdown_type": bt, "breakdown_value": bv,
                "label": _measure_label(std, bt, bv),
                "period_months": months, "period_label": _period_label(months),
                "threshold": config.RELIABILITY_THRESHOLD, "z": config.FUNNEL_LIMITS,
                "national": {"within": within_sum, "total": total_sum, "performance": p0},
                "trusts": trusts,
            }, f, separators=(",", ":"))

        region_clear = (t[~t["sub_threshold"]].groupby("region").size().to_dict())
        measures.append({
            "standard": std, "breakdown_type": bt, "breakdown_value": bv,
            "label": _measure_label(std, bt, bv), "file": fname,
            "n_trusts": len(trusts), "n_threshold": int((~t["sub_threshold"]).sum()),
            "region_threshold_counts": {k: int(v) for k, v in region_clear.items()},
        })

    catalogue = {
        "period_months": months, "period_label": _period_label(months),
        "threshold": config.RELIABILITY_THRESHOLD,
        "window_months": config.COMPARISON_WINDOW_MONTHS, "z": config.FUNNEL_LIMITS,
        "regions": config.NHS_REGIONS, "region_min_trusts": config.REGION_MIN_TRUSTS,
        "comparability_break": config.COMPARABILITY_BREAK,
        "standards": {k: v["label"] for k, v in config.STANDARDS.items()},
        "targets": {k: v["target"] for k, v in config.STANDARDS.items()},
        "measures": sorted(measures, key=lambda m: (m["standard"], m["breakdown_type"], m["breakdown_value"])),
    }
    with open(os.path.join(compare_dir, "index.json"), "w") as f:
        json.dump(catalogue, f, separators=(",", ":"))
    return {"period_months": months, "period_label": _period_label(months),
            "n_measures": len(measures)}


def _build_downloads(df, out_dir):
    """Targeted CSV slices + gzipped full file (replaces the single 200MB CSV)."""
    dl_dir = os.path.join(out_dir, "downloads")
    os.makedirs(dl_dir, exist_ok=True)
    full = df.sort_values(["org_code", "standard", "month"])
    files = []

    for label, g in full.groupby(full["month"].map(_financial_year)):
        name = f"cwt_tidy_{label}.csv"
        g.to_csv(os.path.join(dl_dir, name), index=False)
        files.append(name)

    full[full["breakdown_type"] == "all"].to_csv(
        os.path.join(dl_dir, "cwt_headline_all_cancers.csv"), index=False)
    files.append("cwt_headline_all_cancers.csv")

    with gzip.open(os.path.join(dl_dir, "cwt_tidy_full.csv.gz"), "wt", newline="") as f:
        full.to_csv(f, index=False)
    files.append("cwt_tidy_full.csv.gz")

    with open(os.path.join(dl_dir, "index.json"), "w") as f:
        json.dump({"files": sorted(files)}, f, indent=2)
    return files


def build(df, out_dir=config.SITE_DATA_DIR):
    os.makedirs(os.path.join(out_dir, "org"), exist_ok=True)

    # Per-org files + index
    index = []
    for (code, name, level), g in df.groupby(["org_code", "org_name", "org_level"]):
        if _is_placeholder(code, name):
            continue  # kept in the store/national totals, just not selectable
        region = g["region"].iloc[0]
        payload = _org_payload(g)
        payload.update({"code": code, "name": name, "level": level, "region": region})
        with open(os.path.join(out_dir, "org", f"{code}.json"), "w") as f:
            json.dump(payload, f, separators=(",", ":"))
        if level != "national":
            index.append({"code": code, "name": name, "level": level, "region": region})
    index.sort(key=lambda r: r["name"])
    with open(os.path.join(out_dir, "index.json"), "w") as f:
        json.dump(index, f, separators=(",", ":"))

    # National series as its own file (comparison overlay)
    nat = df[df["org_level"] == "national"]
    if len(nat):
        code = nat["org_code"].iloc[0]
        national_payload = _org_payload(nat)
        with open(os.path.join(out_dir, "national.json"), "w") as f:
            json.dump(national_payload, f, separators=(",", ":"))

    # Trust comparison datasets (funnel / percentile) + targeted downloads
    comparison = _build_comparison(df, out_dir)
    downloads = _build_downloads(df, out_dir)

    # Metadata
    meta = {
        "built_at": dt.datetime.utcnow().isoformat() + "Z",
        "comparability_break": config.COMPARABILITY_BREAK,
        "n_orgs": len(index),
        "months": sorted(df["month"].unique().tolist()),
        "standards": {k: v["label"] for k, v in config.STANDARDS.items()},
        "comparison": comparison,
        "downloads": downloads,
        "note": ("31-day and 62-day standards changed in October 2023; figures "
                 "before that month are not directly comparable."),
    }
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return meta
