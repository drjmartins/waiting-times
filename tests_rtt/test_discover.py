"""Offline tests for RTT source discovery (no network)."""
import datetime as dt

from pipeline_rtt import discover


SAMPLE_HTML = '''
<a href="https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/05/Full-CSV-data-file-Mar26-ZIP-4M-Dc1i9U.zip">Full CSV data file Mar26 (ZIP, 4M)</a>
<a href="https://www.england.nhs.uk/.../Full-CSV-data-file-Apr25-ZIP-4M-revised.zip">Apr25 revised</a>
<a href="https://www.england.nhs.uk/.../Incomplete-Provider-Mar26.xlsx">not a full-csv link</a>
'''


def test_discover_links_parses_month_and_url():
    links = discover.discover_links([SAMPLE_HTML])
    assert links["2026-03"].endswith("Full-CSV-data-file-Mar26-ZIP-4M-Dc1i9U.zip")
    assert "2025-04" in links
    assert len(links) == 2                       # the .xlsx is ignored


def test_financial_years_through_current():
    fys = discover.financial_years(today=dt.date(2026, 6, 20))
    assert fys == ["2022-23", "2023-24", "2024-25", "2025-26", "2026-27"]
    # before April, the current FY started the previous calendar year
    assert discover.financial_years(today=dt.date(2026, 2, 1))[-1] == "2025-26"


def test_select_to_fetch_skips_unchanged(tmp_path):
    links = {"2026-03": "u3", "2026-02": "u2"}
    # 2026-02 present locally + manifest URL matches -> skip; 2026-03 missing -> fetch
    (tmp_path / "2026-02.zip").write_text("x")
    manifest = {"months": {"2026-02": "u2", "2026-03": "u_old"}}
    todo = discover.select_to_fetch(links, manifest, raw_dir=str(tmp_path))
    assert set(todo) == {"2026-03"}              # 2026-02 unchanged+present -> skipped


# --- discover_links_with_retry: added 2026-09-18 after the RTT cron failed
# 2026-09-16/17 when all 5 FY pages returned 200 with zero of the expected
# links (a transient NHS/CloudFront empty-content glitch, not a real page
# format change — confirmed by re-fetching the identical URLs the next day).

def test_discover_links_with_retry_recovers_from_transient_empty(monkeypatch):
    """First scrape of the (single) FY page comes back with no matching
    links; the second attempt gets the real content and recovers."""
    calls = {"n": 0}

    def fake_fetch(url):
        calls["n"] += 1
        if calls["n"] == 1:
            return "<html>nothing here today</html>"
        return SAMPLE_HTML

    monkeypatch.setattr(discover, "fetch_page_html", fake_fetch)

    links = discover.discover_links_with_retry(["2026-27"], attempts=3,
                                                 sleep_fn=lambda s: None)

    assert calls["n"] == 2                       # recovered on attempt 2, didn't need 3
    assert len(links) == 2                        # the real SAMPLE_HTML content


def test_discover_links_with_retry_gives_up_after_persistent_empty(monkeypatch):
    """Every attempt comes back empty (e.g. a genuine, lasting change) — the
    retry must not paper over that: it exhausts its attempts and hands back
    the empty dict for run.py's fail-loud guard to raise on."""
    calls = {"n": 0}

    def fake_fetch(url):
        calls["n"] += 1
        return "<html>still nothing</html>"

    monkeypatch.setattr(discover, "fetch_page_html", fake_fetch)

    links = discover.discover_links_with_retry(["2026-27"], attempts=3,
                                                 sleep_fn=lambda s: None)

    assert links == {}
    assert calls["n"] == 3                        # used every attempt, no more


def test_discover_links_with_retry_first_page_ok_no_retry_needed(monkeypatch):
    """The common case: links present on the first pass across multiple FY
    pages — no retry, one fetch per page, no sleep."""
    calls = {"n": 0}
    sleeps = []

    def fake_fetch(url):
        calls["n"] += 1
        return SAMPLE_HTML

    monkeypatch.setattr(discover, "fetch_page_html", fake_fetch)

    links = discover.discover_links_with_retry(["2025-26", "2026-27"], attempts=3,
                                                 sleep_fn=sleeps.append)

    assert calls["n"] == 2                        # one fetch per FY page, no retry round
    assert len(links) == 2
    assert sleeps == []
