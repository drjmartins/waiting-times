"""Shared ODS (Organisation Data Service) org-status classification.

ONE source of truth for BOTH dashboards: an ICB/trust is "former" regardless of
which dashboard you view it in, so the classification lives in a single shared
cache file (CACHE_PATH) that the cancer and RTT builds both annotate against.

What it produces, per org code that is touched by a merger/closure:

    {"<CODE>": {
        "name": "NHS FRIMLEY INTEGRATED CARE BOARD",
        "status": "former" | "current",
        "closed":  "2026-04-01" | null,   # supersession / legal-close date
        "opened":  "2026-04-01" | null,   # creation date (for newly-formed orgs)
        "successors":   [{"code": "...", "name": "..."}, ...],
        "predecessors": [{"code": "...", "name": "..."}, ...]}}

Only succession-affected orgs (those with a predecessor/successor link, or that
are ODS-Inactive) appear in the cache. Any code ABSENT from the cache is treated
as CURRENT/visible by the builds — fail-open, never drop an org.

KEY DESIGN POINT (verified live 2026-06): ODS keeps a closed org operationally
`Status: Active` through a ~6-month migration overlap, so Status alone MISSES a
just-happened merger. We therefore classify FORMER from the SUCCESSION LINK with a
legal start date that has already passed (with Status==Inactive as a catch-all for
orgs already past their overlap).

FAIL-SOFT: `refresh_or_cache()` tries a live fetch; on ANY failure (network, HTTP,
schema drift) it logs a warning and returns the last-known committed cache, so the
daily data update never crashes and never silently loses orgs. The cache is stamped
only with an ODS-derived `as_of` (max LastChangeDate seen), never a per-run
timestamp, so it commits only when ODS itself changed (respects the CI
no-op-commit guard).
"""
import datetime as dt
import json
import os
import urllib.request

# Single shared cache, read+written by both pipelines (committed to git).
CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "ods_classification.json")

# Public, no-auth ODS Organisation Reference Data (ORD) REST API.
ORD_BASE = "https://directory.spineservices.nhs.uk/ORD/2-0-0"

# Primary role IDs whose orgs we classify. Org-type-AGNOSTIC by design: the same
# succession mechanism covers any statutory org — widen this list (e.g. a new
# provider role) and trust/provider mergers are picked up with no other change.
ROLES = {
    "RO261": "ICB",        # Integrated Care Board (commissioner level)
    "RO197": "NHS Trust",  # NHS Trust + NHS Foundation Trust (provider level)
}

# A code is fetched in full (for its succession links) only if it is Inactive or
# changed within this window — keeps live full-record GETs to a few dozen, not 600+.
# 18 months comfortably spans ODS's ~6-month operational overlap plus buffer.
RECENT_CHANGE_MONTHS = 18

_UA = {"User-Agent": "waiting-times-dashboard/1.0 (+ods-classification)"}


def _get_json(url, timeout=30):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _role_summary(role):
    """{code: {name, status, lastchange}} for one primary role (one API call)."""
    url = f"{ORD_BASE}/organisations?PrimaryRoleId={role}&Limit=1000"
    out = {}
    for o in _get_json(url).get("Organisations", []):
        code = o.get("OrgId")
        if code:
            out[code] = {"name": o.get("Name", code),
                         "status": o.get("Status", "Active"),
                         "lastchange": o.get("LastChangeDate", "")}
    return out


def _full_record(code):
    return _get_json(f"{ORD_BASE}/organisations/{code}").get("Organisation", {})


def _legal_dates(org):
    """(legal_start, legal_end) ISO strings or None, from an org's Date list."""
    start = end = None
    for d in org.get("Date", []):
        if d.get("Type") == "Legal":
            start, end = d.get("Start"), d.get("End")
    return start, end


def _succ_links(org):
    """[(rel_type, target_code, link_start_iso), ...] from an org's Succs list."""
    links = []
    for s in org.get("Succs", {}).get("Succ", []):
        tgt = s.get("Target", {}).get("OrgId", {}).get("extension")
        if not tgt:
            continue
        ds = s.get("Date", [{}])
        start = ds[0].get("Start") if ds else None
        links.append((s.get("Type"), tgt, start))
    return links


def refresh(today=None):
    """Live-fetch the classification from ODS. Raises on any fetch error (the
    caller decides whether to fall back to cache)."""
    today = today or dt.date.today().isoformat()
    cutoff = (dt.date.fromisoformat(today)
              - dt.timedelta(days=int(RECENT_CHANGE_MONTHS * 30.5))).isoformat()

    # One summary call per role -> {code: {name,status,lastchange}}.
    summary = {}
    for role in ROLES:
        summary.update(_role_summary(role))

    def name_of(code):
        return summary.get(code, {}).get("name", code)

    # Candidates for full fetch: anything Inactive or recently changed (covers a
    # merger both during the operational-overlap window and after it goes Inactive).
    candidates = [c for c, s in summary.items()
                  if s["status"] != "Active" or (s["lastchange"] and s["lastchange"] >= cutoff)]

    orgs = {}
    max_change = ""
    for code in candidates:
        org = _full_record(code)
        links = _succ_links(org)
        status_inactive = org.get("Status") == "Inactive"
        if not links and not status_inactive:
            continue  # active org with no succession history — nothing to record
        legal_start, legal_end = _legal_dates(org)
        successors = [{"code": t, "name": name_of(t)} for ty, t, _ in links if ty == "Successor"]
        predecessors = [{"code": t, "name": name_of(t)} for ty, t, _ in links if ty == "Predecessor"]
        # FORMER if any successor link's legal start has passed, or ODS marks it Inactive.
        passed_succ = [st for ty, t, st in links if ty == "Successor" and st and st <= today]
        is_former = bool(passed_succ) or status_inactive
        # Supersession date: earliest passed successor link, else legal end date.
        closed = min(passed_succ) if passed_succ else (legal_end if is_former else None)
        # Creation date for newly-formed orgs (have predecessors): the org's legal start.
        opened = legal_start if predecessors else None
        orgs[code] = {
            "name": org.get("Name", name_of(code)),
            "status": "former" if is_former else "current",
            "closed": (closed.split("T")[0] if closed else None),
            "opened": (opened.split("T")[0] if opened else None),
            "successors": successors,
            "predecessors": predecessors,
        }
        # as_of tracks only STORED (succession-affected) orgs, so the cache commits
        # when a relevant org changes — not on every unrelated ICB/trust edit.
        max_change = max(max_change, summary[code]["lastchange"])
    return {"source": "ODS ORD API", "as_of": max_change, "orgs": orgs}


def is_former(ce):
    """True if this org's classification record marks it former/superseded."""
    return bool(ce and ce.get("status") == "former")


def annotate_entry(entry, ce):
    """Stamp a dashboard index entry with the ODS lifecycle fields the front-ends
    use for the Former-organisations group + generic reciprocal change notes.
    `ce` is this org's classification record (or None → leave as a current org).
    Shared by BOTH dashboards so the picker behaves identically."""
    if not ce:
        return
    if ce.get("status") == "former":
        entry["former"] = True
        if ce.get("closed"):
            entry["closed"] = ce["closed"]
        if ce.get("successors"):            # "Closed … — see related organisations: …"
            entry["related"] = ce["successors"]
            entry["reltype"] = "superseded"
    elif ce.get("predecessors"):            # newly-formed org: "Formed … — see related: …"
        entry["related"] = ce["predecessors"]
        entry["reltype"] = "formed"
        if ce.get("opened"):
            entry["opened"] = ce["opened"]


def load(path=CACHE_PATH):
    """Last-known classification from the committed cache, or empty if none."""
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            print(f"  ODS: cache unreadable ({e}); treating as empty")
    return {"source": "ODS ORD API", "as_of": "", "orgs": {}}


def _write(data, path=CACHE_PATH):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def refresh_or_cache(path=CACHE_PATH, today=None):
    """Fetch live and persist; on ANY failure fall back to the committed cache.
    Returns the orgs dict {code: {...}} (empty if neither source is available).
    Never raises — the data update must not crash on an ODS outage."""
    try:
        data = refresh(today=today)
        _write(data, path)
        n_former = sum(1 for v in data["orgs"].values() if v["status"] == "former")
        print(f"  ODS: classified {len(data['orgs'])} succession-affected orgs "
              f"({n_former} former), as_of {data['as_of'] or 'n/a'}")
        return data["orgs"]
    except Exception as e:
        cached = load(path)
        print(f"  ODS: live fetch failed ({e}); using last-known cache "
              f"({len(cached['orgs'])} orgs, as_of {cached.get('as_of') or 'n/a'})")
        return cached["orgs"]


if __name__ == "__main__":
    # Standalone refresh (handy for CI / manual checks). Never fails the caller.
    orgs = refresh_or_cache()
    formers = sorted(c for c, v in orgs.items() if v["status"] == "former")
    print(f"former: {formers}")
