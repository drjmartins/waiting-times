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
from . import cancer_groups

# Non-real placeholder orgs (e.g. the 'UNKNOWN' unallocated-commissioner bucket).
# Hidden from the picker and comparison view, but RETAINED in the tidy store and
# in national totals so sums still reconcile.
PLACEHOLDER_NAMES = {"UNKNOWN"}


def _is_placeholder(code, name):
    return (str(code).strip().upper() in PLACEHOLDER_NAMES
            or str(name).strip().upper() in PLACEHOLDER_NAMES)


def _negligible_orgs(df):
    """Codes to HIDE from the picker / default lists (selection-only: the per-org
    files are still written, the org stays in the store + downloads, and a direct
    ?org= link still resolves and renders with the usual low-reliability flags).

    Computed DYNAMICALLY from the current data each build — not a frozen list — so
    an org that crosses the bar (or a brand-new org) appears automatically and a
    dormant one drops. Rules (confirmed against the activity distribution, see
    DECISIONS.md 2026-06-12; the data separates cleanly):
      * PROVIDER hidden if NO standard clears the reliability threshold (n>=10) in a
        single month within the last config.PICKER_PROVIDER_WINDOW_MONTHS — i.e.
        negligible RECENT activity (incl. dormant / defunct-merged codes). The
        full-year window avoids the reporting-lag false positives a shorter window
        would wrongly hide;
      * COMMISSIONER hidden if its recent-3-finalised-month pooled all-cancers
        denominator (summed across standards) is below
        config.PICKER_MIN_COMMISSIONER_DENOM — isolates the commissioning hubs.
    Placeholders are already excluded elsewhere; skip them here too."""
    allrows = df[df["breakdown_type"] == "all"]
    recent = set(_recent_final_months(df))
    all_months = sorted(df["month"].unique())
    provider_window = set(all_months[-config.PICKER_PROVIDER_WINDOW_MONTHS:])
    hidden = set()
    for (code, name, level), g in allrows.groupby(["org_code", "org_name", "org_level"]):
        if _is_placeholder(code, name):
            continue
        if level == "provider":
            recent_g = g.loc[g["month"].isin(provider_window), "total"]
            if recent_g.empty or recent_g.max() < config.RELIABILITY_THRESHOLD:
                hidden.add(code)
        elif level == "icb":
            if g.loc[g["month"].isin(recent), "total"].sum() < config.PICKER_MIN_COMMISSIONER_DENOM:
                hidden.add(code)
    return hidden


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


# Breakdown dimensions exported in the load-on-demand per-org breakdown file.
# The file carries every dimension that exists in the source; which ones are
# *offered* per standard is a front-end concern (FDS28 surfaces cancer only).
BREAKDOWN_DIMS = ("cancer", "route", "modality", "combination")

# Fraction-of-group-activity bar below which a (cancer_group, route) slice is
# treated as not-applicable noise and omitted. The data separates cleanly: a
# route that genuinely applies to a group is 3-82% of that group's activity,
# whereas a cancer-specific route appearing under the wrong group (e.g. Breast
# Symptomatic under Lung, or Screening under Skin) is 0.0-0.1% — structural
# miscoding, ~1 patient/month. 1% sits squarely in that gap. See DECISIONS.md
# (2026-06-11 route-characterisation finding).
GROUP_ROUTE_ACTIVITY_BAR = 0.01


def _cancer_group_slices(cancer_rows):
    """Aggregate raw 'cancer' breakdown rows into NHS England's ten tumour-site
    groups for one (org, standard). Per (group, month) we SUM the numerators and
    SUM the denominators across the constituent cancer types, THEN compute
    performance from the totals — never average the per-type percentages
    (mis-weights types of different sizes). Returns slices keyed by group name,
    same series shape as the raw dims. Empty groups (no constituent rows for this
    org/standard) are omitted, so the front end can treat an absent group as
    'not published here' rather than a flat-zero line."""
    if cancer_rows.empty:
        return {}
    rows = cancer_rows.copy()
    rows["group"] = rows["breakdown_value"].map(cancer_groups.group_for)

    # Build-time double-count guard: a parent label and its children must never
    # share a (month) cell, or the group denominator would double. Cheap insurance
    # against a future NHS vintage shifting granularity mid-series.
    for _m, mg in rows.groupby("month"):
        cancer_groups.assert_no_double_count(mg["breakdown_value"].tolist())

    agg = (rows.groupby(["group", "month"], as_index=False)
               .agg(within=("within_target", "sum"),
                    total=("total", "sum"),
                    # within a (month, org, standard) all cancer rows come from one
                    # source file → one status; 'min' keeps provisional if ever mixed.
                    data_status=("data_status", "min")))
    agg["performance"] = (agg["within"] / agg["total"]).round(4)

    slices = {}
    for grp in cancer_groups.TEN_GROUPS:
        g = agg[agg["group"] == grp].sort_values("month")
        if g.empty:
            continue
        slices[grp] = {
            "months": g["month"].tolist(),
            "performance": g["performance"].tolist(),
            "within_target": [_num(v) for v in g["within"]],
            "total": [_num(v) for v in g["total"]],
            "data_status": g["data_status"].tolist(),
        }
    return slices


def _cancer_group_route_slices(srows, route_values, cancer_values):
    """For one (org, standard): roll the cancer x route combination rows up into
    NHS's ten tumour-site groups x route. Per (group, route, month) SUM numerators
    and denominators across the group's constituent cancer types, THEN compute
    performance from the totals (never average per-type percentages). Returns
    {group: {route: <series>, ...}, ...} — the shape the group-aware route dropdown
    consumes (v6).

    Routes are PARTLY cancer-specific (Breast Symptomatic -> Breast only; Screening
    -> the screening-programme cancers), and the source ships near-zero noise cells
    for the impossible cross-tabs. So a (group, route) slice is emitted ONLY when
    its cumulative denominator clears GROUP_ROUTE_ACTIVITY_BAR of the group's total
    route activity, computed PER ORG — a small trust legitimately surfaces fewer
    routes than the national picture, and the front end just lists what is present.

    Reconciliation guard (fail-loud, protects the daily CI refresh): for every
    (group, month) the routes must sum to that group's cancer total — verified
    exact in the real source — so a future NHS vintage that breaks the route
    partition fails the run rather than shipping a wrong denominator."""
    if not route_values:
        return {}
    comb = srows[srows["breakdown_type"] == "combination"]
    if comb.empty:
        return {}
    split = comb["breakdown_value"].str.split("|", n=1, expand=True)
    if split.shape[1] < 2:
        return {}
    rows = comb.assign(_a=split[0].str.strip(), _b=split[1].str.strip())
    rows = rows[rows["_a"].isin(cancer_values) & rows["_b"].isin(route_values)]
    if rows.empty:
        return {}
    rows = rows.assign(group=rows["_a"].map(cancer_groups.group_for))

    agg = (rows.groupby(["group", "_b", "month"], as_index=False)
               .agg(within=("within_target", "sum"),
                    total=("total", "sum"),
                    data_status=("data_status", "min")))

    # Reconciliation guard (fail-loud, protects the daily refresh, which rebuilds
    # newly-fetched data AFTER the pre-fetch test gate). We assert the SAFETY-
    # CRITICAL direction: a group's routes must never EXCEED its cancer total
    # (inflation / double-counting → a wrong, overstated denominator). Real NHS
    # data partitions EXACTLY (routes == total; asserted in tests against the
    # store); an under-count (routes < total) only ever means a route is missing
    # and degrades gracefully (one fewer option), so it isn't a build-stopper and
    # keeps minimal unit fixtures — which carry partial combos — valid.
    canc = srows[srows["breakdown_type"] == "cancer"].copy()
    canc["group"] = canc["breakdown_value"].map(cancer_groups.group_for)
    grp_tot = canc.groupby(["group", "month"])["total"].sum()
    rte_tot = agg.groupby(["group", "month"])["total"].sum()
    over = rte_tot.subtract(grp_tot, fill_value=0)        # routes minus group total
    if (over > 0.6).any():
        bad = over[over > 0.6]
        raise AssertionError(
            "cancer_group x route EXCEEDS the group cancer total (double-count?) "
            f"(max over {over.max()}): {bad.head().to_dict()}")

    agg["performance"] = (agg["within"] / agg["total"]).round(4)
    out = {}
    for grp in cancer_groups.TEN_GROUPS:
        g = agg[agg["group"] == grp]
        denom = g["total"].sum()
        if denom <= 0:
            continue
        bar = GROUP_ROUTE_ACTIVITY_BAR * denom
        routes = {}
        for rv, rg in g.groupby("_b"):
            if rg["total"].sum() < bar:
                continue                       # cancer-specific route under the wrong group: drop the noise
            rg = rg.sort_values("month")
            routes[str(rv)] = {
                "months": rg["month"].tolist(),
                "performance": rg["performance"].tolist(),
                "within_target": [_num(v) for v in rg["within"]],
                "total": [_num(v) for v in rg["total"]],
                "data_status": rg["data_status"].tolist(),
            }
        if routes:
            out[grp] = routes
    return out


def _breakdown_payload(df_org):
    """Per-org breakdown series for every standard. Carries the raw granular
    dimensions (cancer / route / modality + published pairwise combinations) AND
    a new 'cancer_group' dimension: NHS England's ten tumour-site groups, summed
    up from the raw cancer types (kept ALONGSIDE the granular cancer dim, not as
    a replacement). Same series shape throughout so the front end renders any of
    them with no new chart code. Shipped as a separate org/<CODE>.breakdown.json
    fetched ONLY when the user opens a filter / picks a group."""
    out = {"standards": {}}
    for std in config.STANDARDS:
        srows = df_org[df_org["standard"] == std]
        dims = {}
        for bt in BREAKDOWN_DIMS:
            rows = srows[srows["breakdown_type"] == bt]
            if rows.empty:
                continue
            slices = {}
            for bv, g in rows.groupby("breakdown_value"):
                g = g.sort_values("month")
                slices[str(bv)] = {
                    "months": g["month"].tolist(),
                    "performance": g["performance"].tolist(),
                    "within_target": [_num(v) for v in g["within_target"]],
                    "total": [_num(v) for v in g["total"]],
                    "data_status": g["data_status"].tolist(),
                }
            if slices:
                dims[bt] = slices
        # NHS ten-group rollup, derived from the raw cancer rows.
        group_slices = _cancer_group_slices(srows[srows["breakdown_type"] == "cancer"])
        if group_slices:
            dims["cancer_group"] = group_slices
        # Group-aware routes (v6): ten groups x route, activity-filtered so a group
        # only offers the routes that genuinely apply to it. Built from the
        # cancer x route combos; absent for FDS28 (no route dim).
        group_route = _cancer_group_route_slices(
            srows,
            set(dims.get("route", {}).keys()),
            set(dims.get("cancer", {}).keys()))
        if group_route:
            dims["cancer_group_route"] = group_route
        if dims:
            out["standards"][std] = dims
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


def _num(v):
    """NHS small-number rounding leaves fractional values (e.g. 0.5); keep them
    truthful rather than truncating 0.5 -> 0, but show whole counts as ints."""
    v = float(v)
    return int(v) if v.is_integer() else round(v, 1)


def _overdispersion(t, p0):
    """
    Winsorised multiplicative overdispersion factor phi (after Spiegelhalter).
    Plain binomial limits assume every trust is otherwise identical and so flag
    a large share of trusts at large denominators; phi widens the limits to
    reflect genuine between-trust variation. Estimated from threshold-clearing
    units only (a 0.5-patient unit has no business setting the dispersion), and
    Winsorised at the 10th/90th percentiles so a few extreme trusts don't blow
    it up. Returns phi >= 1 (1.0 = no overdispersion / fall back to binomial).
    """
    if p0 is None or not (0 < p0 < 1):
        return 1.0
    rel = t[t["total"] >= config.RELIABILITY_THRESHOLD]
    if len(rel) < 3:
        return 1.0
    se = (p0 * (1 - p0) / rel["total"]) ** 0.5
    z = ((rel["performance"] - p0) / se).sort_values().reset_index(drop=True)
    n = len(z)
    lo, hi = z.iloc[int(0.10 * n)], z.iloc[min(n - 1, int(0.90 * n))]
    phi = float((z.clip(lo, hi) ** 2).mean())
    return round(max(1.0, phi), 3)


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
        within_sum, total_sum = float(t["within"].sum()), float(t["total"].sum())
        p0 = round(within_sum / total_sum, 4) if total_sum else None
        phi = _overdispersion(t, p0)

        fname = f"{std}__{bt}__{_slug(bv)}.json"
        n = 2
        while fname in used:  # guarantee unique filenames across breakdown values
            fname = f"{std}__{bt}__{_slug(bv)}-{n}.json"
            n += 1
        used.add(fname)

        trusts = [{"code": r.org_code, "name": r.org_name, "region": r.region,
                   "within": _num(r.within), "total": _num(r.total),
                   "performance": r.performance, "sub_threshold": bool(r.sub_threshold)}
                  for r in t.sort_values("total", ascending=False).itertuples()]
        with open(os.path.join(compare_dir, fname), "w") as f:
            json.dump({
                "standard": std, "breakdown_type": bt, "breakdown_value": bv,
                "label": _measure_label(std, bt, bv),
                "period_months": months, "period_label": _period_label(months),
                "threshold": config.RELIABILITY_THRESHOLD, "z": config.FUNNEL_LIMITS,
                "overdispersion": {"phi": phi, "winsorised": True,
                                   "n_units": int((t["total"] >= config.RELIABILITY_THRESHOLD).sum())},
                "national": {"within": _num(within_sum), "total": _num(total_sum), "performance": p0},
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
    # Fail loudly if a composite group's composition description has drifted from
    # the actual cancer_groups mapping before we emit it into meta.json (v7).
    cancer_groups.assert_composition_consistent()
    os.makedirs(os.path.join(out_dir, "org"), exist_ok=True)

    # Negligible-activity orgs to hide from the picker (computed each build). They
    # still get per-org files written and stay in index.json flagged hidden=true,
    # so direct ?org= links resolve; the front end just filters them out of the
    # picker / default lists.
    hidden = _negligible_orgs(df)

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
            # Load-on-demand breakdown file (gitignored, rebuilt every run).
            with open(os.path.join(out_dir, "org", f"{code}.breakdown.json"), "w") as f:
                json.dump(_breakdown_payload(g), f, separators=(",", ":"))
            entry = {"code": code, "name": name, "level": level, "region": region}
            if code in hidden:
                entry["hidden"] = True   # negligible activity: out of the picker, still direct-linkable
            index.append(entry)
    index.sort(key=lambda r: r["name"])
    with open(os.path.join(out_dir, "index.json"), "w") as f:
        json.dump(index, f, separators=(",", ":"))
    n_hidden = {
        "providers": sum(1 for e in index if e.get("hidden") and e["level"] == "provider"),
        "commissioners": sum(1 for e in index if e.get("hidden") and e["level"] == "icb"),
    }
    n_selectable = sum(1 for e in index if not e.get("hidden"))

    # National series as its own file (comparison overlay)
    nat = df[df["org_level"] == "national"]
    if len(nat):
        code = nat["org_code"].iloc[0]
        national_payload = _org_payload(nat)
        with open(os.path.join(out_dir, "national.json"), "w") as f:
            json.dump(national_payload, f, separators=(",", ":"))
        # National breakdown (for the slice-matched comparison line, on demand).
        with open(os.path.join(out_dir, "national.breakdown.json"), "w") as f:
            json.dump(_breakdown_payload(nat), f, separators=(",", ":"))

    # Trust comparison datasets (funnel / percentile) + targeted downloads
    comparison = _build_comparison(df, out_dir)
    downloads = _build_downloads(df, out_dir)

    # Metadata
    meta = {
        "built_at": dt.datetime.utcnow().isoformat() + "Z",
        "comparability_break": config.COMPARABILITY_BREAK,
        "n_orgs": n_selectable,                       # selectable in the picker
        "n_orgs_total": len(index),                   # incl. hidden (direct-linkable)
        "hidden_from_picker": n_hidden,
        "months": sorted(df["month"].unique().tolist()),
        "standards": {k: v["label"] for k, v in config.STANDARDS.items()},
        "comparison": comparison,
        "downloads": downloads,
        # Composite-group make-up, sourced from cancer_groups so the front-end
        # description can't drift from the actual mapping (v7). Composite groups
        # only; the six 1:1 groups are self-explanatory and absent here.
        "group_composition": {g: cancer_groups.composition_text(g)
                              for g in cancer_groups.COMPOSITE_GROUPS},
        "note": ("31-day and 62-day standards changed in October 2023; figures "
                 "before that month are not directly comparable."),
    }
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return meta
