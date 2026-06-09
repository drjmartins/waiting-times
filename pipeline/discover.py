"""
Source discovery + manifest management.

Responsibilities:
  1. Scrape the NHS England CWT page for the "Monthly Combined CSV" links.
  2. Compare against the manifest of what we've already processed.
  3. Return only the files that are new or have changed (revised).

This is what makes the dashboard "automatically pull new data": run it on a
daily schedule; it does real work only when NHS England posts something new.

Network note: in some sandboxes england.nhs.uk is not reachable. The functions
take an optional `html` argument so they can be unit-tested offline.
"""
import json
import os
import re
import datetime as dt
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    requests = None

from . import config


def fetch_page_html(url=config.SOURCE_PAGE):
    """Fetch the source page HTML. Raises if network unavailable."""
    if requests is None:
        raise RuntimeError("requests not installed")
    resp = requests.get(url, timeout=60, headers={"User-Agent": "cwt-dashboard/1.0"})
    resp.raise_for_status()
    return resp.text


def discover_csv_links(html, base_url=config.SOURCE_PAGE):
    """
    Parse anchor tags from the page and return the combined-CSV links.

    Returns a list of dicts: {url, anchor_text, financial_year, status}.
    `status` is inferred from the anchor text ('Provisional'/'Final').
    """
    # Lightweight anchor extraction; avoids a heavy HTML parser dependency.
    anchors = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
    out = []
    for href, text in anchors:
        clean = re.sub(r"<[^>]+>", "", text).strip()
        if not any(m in clean for m in config.COMBINED_CSV_MARKERS):
            continue
        if not href.lower().endswith(".csv"):
            continue
        fy = _extract_financial_year(clean)
        status = "final" if "final" in clean.lower() else "provisional"
        out.append({
            "url": urljoin(base_url, href),
            "anchor_text": clean,
            "financial_year": fy,
            "status": status,
        })
    return out


def _extract_financial_year(text):
    m = re.search(r"(\d{4})-(\d{2})", text)
    return f"{m.group(1)}-{m.group(2)}" if m else "unknown"


def load_manifest(path=config.MANIFEST_PATH):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"files": {}, "last_checked": None}


def save_manifest(manifest, path=config.MANIFEST_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    manifest["last_checked"] = dt.datetime.utcnow().isoformat() + "Z"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)


def select_files_to_process(discovered, manifest):
    """
    Decide which discovered files need processing.

    A file is processed if:
      - its URL is new (never seen), OR
      - its status changed (provisional -> final), OR
      - the URL changed for a financial year we already have (a revision: NHS
        re-uploads with a new date in the path).
    """
    seen = manifest.get("files", {})
    seen_by_fy = {v["financial_year"]: (u, v) for u, v in seen.items()}
    to_process = []
    for item in discovered:
        url = item["url"]
        if url in seen:
            continue  # identical URL already done
        prev = seen_by_fy.get(item["financial_year"])
        if prev is None:
            item["reason"] = "new financial year"
        elif prev[1]["status"] != item["status"]:
            item["reason"] = f"status change {prev[1]['status']} -> {item['status']}"
        else:
            item["reason"] = "revised upload (new URL, same FY/status)"
        to_process.append(item)
    return to_process
