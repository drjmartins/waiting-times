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


_MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
           "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
           "november": 11, "december": 12}


def current_financial_year(today=None):
    """The current NHS financial year as an 'N-(N+1)' slug (April N .. March N+1).
    Mirrors pipeline_rtt's convention so the cancer pipeline can scrape the current
    FY's per-month sub-page the moment a new year opens."""
    today = today or dt.date.today()
    start = today.year if today.month >= 4 else today.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def fy_subpage_url(fy):
    return config.SOURCE_FY_PAGE_TEMPLATE.format(fy=fy)


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

    Returns a list of dicts: {url, anchor_text, financial_year, status, shape, month}.
    `status` is inferred from the anchor text ('Provisional'/'Final'). `shape` is
    'cumulative' (the per-FY files on the main page) or 'monthly' (the per-month
    files on an FY sub-page), classified from the FILENAME: cumulative files are
    FY-prefixed ('2025-26-…'), per-month files are month-name-prefixed
    ('April-2026-…'). `month` is the per-month file's 'YYYY-MM' (None for
    cumulative, or None for a monthly-shaped file whose filename could not be
    parsed — a state run.py refuses to ingest, the fail-loud month-label guard).
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
        url = urljoin(base_url, href)
        basename = url.rsplit("/", 1)[-1]
        shape, month = _classify_file(basename)
        # FY: a per-month file derives its FY from its month; a cumulative file
        # carries the FY in its anchor/filename text.
        fy = _fy_for_month(month) if month else _extract_financial_year(clean)
        status = "final" if "final" in clean.lower() else "provisional"
        out.append({
            "url": url,
            "anchor_text": clean,
            "financial_year": fy,
            "status": status,
            "shape": shape,
            "month": month,
        })
    return out


def _classify_file(basename):
    """(shape, month) from a Combined-CSV filename.

    Cumulative files are FY-prefixed ('2025-26-Apr-Sep-…', '2024-25-Apr-Mar-…').
    Per-month files are full-month-name-prefixed ('April-2026-Monthly-Combined-…').
    A per-month-shaped name that doesn't cleanly parse returns ('monthly', None);
    run.py turns that into a fail-loud refusal rather than guessing a month."""
    if re.match(r"\d{4}-\d{2}-", basename):
        return "cumulative", None
    m = re.match(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"[-_ ](\d{4})\b",
        basename, re.IGNORECASE)
    if m:
        return "monthly", f"{int(m.group(2))}-{_MONTHS[m.group(1).lower()]:02d}"
    # Anything else that reached here is a Combined CSV we don't recognise the
    # vintage of; treat as monthly-with-unparseable-month so the guard fires.
    return "monthly", None


def _fy_for_month(month):
    """'YYYY-MM' -> 'N-(N+1)' financial-year slug."""
    y, m = (int(x) for x in month.split("-"))
    start = y if m >= 4 else y - 1
    return f"{start}-{str(start + 1)[-2:]}"


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
