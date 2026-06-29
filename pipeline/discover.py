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
_MONTH_ABBR = {name[:3]: num for name, num in _MONTHS.items()}


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

    A per-month file covers EXACTLY ONE calendar month and carries that month here:
      * plain month-name-prefixed  -> 'April-2026-Monthly-…'      (month 2026-04)
      * FY-prefixed single month   -> '2026-27-Apr-Monthly-…'     (month 2026-04)
        (a re-publication NHS posted at the 2026-27 FY boundary; carries a Period
         column, so normalise reads its month and the filename month cross-checks).
    A cumulative file covers a RANGE of months (month=None; per-month rows come
    from the file's Period column):
      * full FY   -> '2022-23-Apr-Mar-Monthly-…'
      * part FY   -> '2025-26-Apr-Sep-Cumulative-…', '2025-26-Oct-Mar-Cumulative-…'
    A per-month-shaped name that doesn't cleanly parse returns ('monthly', None);
    run.py turns that into a fail-loud refusal rather than guessing a month."""
    # FY-prefixed: tell a single-month re-publication apart from a true cumulative.
    fy = re.match(r"(\d{4})-(\d{2})-(.*)", basename)
    if fy:
        months = [t.lower() for t in re.findall(
            r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*",
            fy.group(3), re.IGNORECASE)]
        # A true cumulative names a month RANGE (>=2 distinct months) or says so.
        if "cumulative" in basename.lower() or len(set(months)) >= 2:
            return "cumulative", None
        if len(months) == 1:
            fy_start = int(fy.group(1))
            mon = _MONTH_ABBR[months[0]]
            year = fy_start if mon >= 4 else fy_start + 1
            return "monthly", f"{year}-{mon:02d}"
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


def dedupe_per_month(discovered):
    """Keep at most ONE per-month file per (month, status).

    NHS sometimes publishes the SAME month under several filenames — decisively at
    the April-2026 ICB-merger boundary, which carried THREE April provisionals: an
    old-structure 'April-2026-Monthly-…', a new-FY-prefixed re-publication
    '2026-27-Apr-Monthly-…', and an explicit '…-New-ICB-Structure' file. Each file
    is individually self-consistent (its ten cancer groups + the Missing/Invalid
    residue reconcile EXACTLY to its all-cancers headline), but ingesting more than
    one UNIONS their breakdown rows wherever the vintages disagree (e.g. a row the
    re-publication dropped lingers from the original) and breaks that exact
    reconciliation — the failure that wedged the cron on 2026-06-27/28.

    We therefore select a single authoritative vintage per (month, status),
    preferring the CURRENT organisational structure the dashboard keys ICBs on (see
    `_vintage_rank`). Cumulative files (month=None — a month RANGE) are passed
    through untouched: they legitimately supply many months and the merge
    precedence (final>provisional, then cumulative>per-month) handles their
    overlaps with per-month files. `merge_with_revisions` is the defence-in-depth
    backstop: it keeps a (month, org, standard) cell single-source even if two
    files ever slip past this."""
    by_key, passthrough = {}, []
    for item in discovered:
        month = item.get("month")
        if not month:                       # cumulative / unparseable -> untouched
            passthrough.append(item)
            continue
        by_key.setdefault((month, item.get("status")), []).append(item)
    kept = []
    for group in by_key.values():
        kept.append(max(group, key=_vintage_rank) if len(group) > 1 else group[0])
    return passthrough + kept


def _vintage_rank(item):
    """Preference key (higher wins) among files covering the SAME month+status.
    Prefer the file reflecting the CURRENT org structure:
      1. an explicit 'New-ICB-Structure' (current-structure) marker, else
      2. the FY-prefixed consolidated re-publication, else
      3. the plain month-prefixed file,
    with the URL as a final deterministic, fetch-order-independent tie-break.
    Choosing any single self-consistent file guarantees exact reconciliation; this
    precedence only decides which ICB geography is shown — and the dashboard's ODS
    lifecycle already treats the 12 pre-merger ICBs as FORMER from April 2026, so
    the new structure is the correct one to surface."""
    name = item["url"].rsplit("/", 1)[-1].lower()
    new_structure = "new-icb-structure" in name or "new_icb_structure" in name
    fy_prefixed = bool(re.match(r"\d{4}-\d{2}-", name))
    return (new_structure, fy_prefixed, item["url"])


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
