"""
Pipeline entry point.

Usage:
  python -m pipeline.run            # real run: scrape NHS, fetch new files, rebuild
  python -m pipeline.run --synthetic # offline demo run with fabricated data

The real run is idempotent and cheap: it only downloads/parses files that are
new or revised since the last run (per the manifest), then rebuilds the site
data from the full accumulated tidy table.
"""
import argparse
import os
import sys

import pandas as pd

from . import config, discover, normalise, build_site_data
from pipeline_common import ods

# Real and synthetic runs MUST use separate stores. They previously shared
# tidy.parquet, so a `--synthetic` dev run would seed the next real run and
# fabricated rows would be merged into genuine NHS data.
TIDY_STORE = os.path.join(config.PROCESSED_DIR, "tidy.parquet")
SYNTHETIC_STORE = os.path.join(config.PROCESSED_DIR, "tidy_synthetic.parquet")


def _load_store(path=TIDY_STORE):
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None


def _save_store(df, path=TIDY_STORE):
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    df.to_parquet(path, index=False)


def run_real():
    import requests
    # Main page: per-FY CUMULATIVE Combined CSVs. Plus the CURRENT FY's sub-page:
    # per-MONTH Combined CSVs that appear there first at a financial-year boundary
    # (closes the FY-boundary staleness gap). The sub-page may not exist yet very
    # early in a new FY — treat a fetch failure there as "no per-month files yet".
    html = discover.fetch_page_html()
    discovered = discover.discover_csv_links(html)
    fy = discover.current_financial_year()
    sub_url = discover.fy_subpage_url(fy)
    try:
        sub_html = discover.fetch_page_html(sub_url)
        discovered += discover.discover_csv_links(sub_html, base_url=sub_url)
    except Exception as e:
        print(f"Current-FY sub-page {sub_url} not available ({e}); "
              f"using main-page cumulative files only.")
    # Collapse multiple vintages of the SAME month to one authoritative file before
    # selection, so a month is never ingested from two disagreeing files (the
    # 2026-04 ICB-merger triple that wedged the cron). Cumulatives pass through.
    discovered = discover.dedupe_per_month(discovered)
    manifest = discover.load_manifest()
    todo = discover.select_files_to_process(discovered, manifest)
    store = _load_store()
    if todo:
        os.makedirs(config.RAW_DIR, exist_ok=True)
        for item in todo:
            print(f"Processing ({item['reason']}): {item['anchor_text']}")
            basename = os.path.basename(item["url"])
            # Fail-loud month-label guard (part 1): a per-month file whose month
            # could not be parsed from its filename is refused — never guessed.
            if item.get("shape") == "monthly" and not item.get("month"):
                raise RuntimeError(
                    f"per-month Combined CSV {basename!r} present but its month could not "
                    f"be parsed from the filename — refusing to ingest (would mislabel the "
                    f"month, and the recon gates can't catch a wrong month label).")
            raw_path = os.path.join(config.RAW_DIR, basename)
            with requests.get(item["url"], stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(raw_path, "wb") as f:
                    for chunk in r.iter_content(1 << 16):
                        f.write(chunk)
            raw = pd.read_csv(raw_path, low_memory=False)
            tidy = normalise.normalise(raw, basename, item["status"], period_hint=item.get("month"))
            # Fail-loud month-label guard (part 2): per-month rows must all carry
            # exactly the filename's month (single, parseable). Skipped for the
            # cumulative path (multi-month by design).
            if item.get("month"):
                normalise.assert_month_label(tidy, item["month"], basename)
            store = normalise.merge_with_revisions(store, tidy)
            manifest["files"][item["url"]] = {
                "financial_year": item["financial_year"], "status": item["status"],
                "anchor_text": item["anchor_text"],
            }
        _save_store(store)
        discover.save_manifest(manifest)
    else:
        print("No new or revised files.")

    if store is None or len(store) == 0:
        print("No data in store and nothing to fetch; skipping build.")
        return
    # Fail-loud series guard (part 3): no duplicate/missing month in the national
    # series across the cumulative<->per-month seam.
    normalise.assert_contiguous_national_months(store)
    # Fail-loud BIDIRECTIONAL reconciliation gate (2026-06-29): the ten groups +
    # Missing/Invalid residue must equal the all-cancers headline, and cancer x
    # route must partition the group total — both exactly, both directions. This
    # is the SAME check the store tests run, so a future vintage-mix fails the
    # build here (before commit) rather than wedging the next run's test gate.
    build_site_data.assert_store_reconciles(store)
    # Shared ODS org-status classification (current/former + succession links) plus
    # the NHS-trust code set for the provider-type filter. Fail-soft: on any ODS
    # outage this returns the last-known committed cache and never raises, so the
    # data update can't crash on the new external dependency.
    ods_data = ods.refresh_or_cache()
    if not ods_data.get("nhs_trust_codes"):
        raise RuntimeError("ODS classification returned no NHS-trust codes (live fetch AND committed "
                           "cache both empty) — refusing to build a provider-type split that would "
                           "mis-show every provider under the NHS-Trusts default.")
    # Always rebuild the site from the current store, even on a no-op fetch:
    # the download slices and comparison JSONs are build artefacts (gitignored,
    # not in the checkout), so the Pages artefact would otherwise ship without
    # them on any run that found no new data.
    meta = build_site_data.build(store, classification=ods_data["orgs"],
                                 trust_codes=set(ods_data.get("nhs_trust_codes") or []))
    print(f"{'Rebuilt' if todo else 'Rebuilt (no new data)'} site data: "
          f"{meta['n_orgs']} orgs, {len(meta['months'])} months.")


def run_synthetic():
    from . import synthetic
    raw = synthetic.generate(start="2023-10", n_months=18)
    tidy = normalise.normalise(raw, "synthetic_combined.csv", "provisional")
    months = sorted(tidy.month.unique())
    tidy.loc[tidy.month.isin(months[:-2]), "data_status"] = "final"
    _save_store(tidy, SYNTHETIC_STORE)
    meta = build_site_data.build(tidy)
    print(f"[synthetic] Built {meta['n_orgs']} orgs, {len(meta['months'])} months.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()
    if args.synthetic:
        run_synthetic()
    else:
        try:
            run_real()
        except Exception as e:
            print(f"Real run failed ({e}).", file=sys.stderr)
            sys.exit(1)
