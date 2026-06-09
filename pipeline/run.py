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
    html = discover.fetch_page_html()
    discovered = discover.discover_csv_links(html)
    manifest = discover.load_manifest()
    todo = discover.select_files_to_process(discovered, manifest)
    if not todo:
        print("No new or revised files. Nothing to do.")
        return
    store = _load_store()
    os.makedirs(config.RAW_DIR, exist_ok=True)
    for item in todo:
        print(f"Processing ({item['reason']}): {item['anchor_text']}")
        raw_path = os.path.join(config.RAW_DIR, os.path.basename(item["url"]))
        with requests.get(item["url"], stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(raw_path, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
        raw = pd.read_csv(raw_path, low_memory=False)
        tidy = normalise.normalise(raw, os.path.basename(item["url"]), item["status"])
        store = normalise.merge_with_revisions(store, tidy)
        manifest["files"][item["url"]] = {
            "financial_year": item["financial_year"], "status": item["status"],
            "anchor_text": item["anchor_text"],
        }
    _save_store(store)
    discover.save_manifest(manifest)
    meta = build_site_data.build(store)
    print(f"Rebuilt site data: {meta['n_orgs']} orgs, {len(meta['months'])} months.")


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
