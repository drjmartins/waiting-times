"""
Tests for the cancer pipeline's bounded-retry discovery wrapper
(pipeline.discover.scrape_all_links_with_retry), added 2026-09-18 as the
symmetric counterpart to pipeline_rtt's fix.

Cancer's discover.py had NO equivalent to RTT's "found nothing — refuse to
build" guard before this change: `run_real()` just printed "No new or
revised files" and rebuilt from the existing store whenever discovery came
back empty, silently. That is indistinguishable from the transient
NHS/CloudFront empty-content glitch RTT hit on 2026-09-16/17 (same domain,
same request pattern) — cancer was equally exposed, it just had no guard to
even notice if it happened. This adds both: the retry (rescues a transient
blip) and the missing fail-loud guard (`pipeline/run.py` now raises if the
main+sub-page scrape is STILL empty after retrying), mirroring RTT exactly.

Guards:
  1. A transient empty scrape (e.g. the main page glitches once) recovers on
     a later attempt without exhausting every try.
  2. A persistently empty scrape still comes back empty after `attempts`
     tries, for run_real()'s new guard to raise on.
"""
from pipeline import discover


MAIN_PAGE_HTML = '''
<a href="/2025-26-Monthly-Combined-CSV.csv">Monthly Combined CSV Final</a>
'''


def test_scrape_all_links_with_retry_recovers_from_transient_empty(monkeypatch):
    """The main page comes back empty on the first attempt (the transient
    glitch); the second attempt gets real content and recovers. The
    current-FY sub-page 404s throughout, which is fine — the guard is on the
    combined main+sub result, not the sub-page alone."""
    calls = {"main": 0}

    def fake_fetch(url=discover.config.SOURCE_PAGE):
        if url == discover.config.SOURCE_PAGE:
            calls["main"] += 1
            return "<html>nothing here today</html>" if calls["main"] == 1 else MAIN_PAGE_HTML
        raise RuntimeError("404 (sub-page not published yet)")

    monkeypatch.setattr(discover, "fetch_page_html", fake_fetch)

    discovered = discover.scrape_all_links_with_retry(attempts=3, sleep_fn=lambda s: None)

    assert calls["main"] == 2                     # recovered on attempt 2, didn't need 3
    assert len(discovered) == 1


def test_scrape_all_links_with_retry_gives_up_after_persistent_empty(monkeypatch):
    """Every attempt's main+sub scrape is empty — the retry must not mask
    that: it exhausts its attempts and hands back the empty list for
    run.py's fail-loud guard to raise on."""
    calls = {"main": 0}

    def fake_fetch(url=discover.config.SOURCE_PAGE):
        if url == discover.config.SOURCE_PAGE:
            calls["main"] += 1
            return "<html>still nothing</html>"
        raise RuntimeError("404 (sub-page not published yet)")

    monkeypatch.setattr(discover, "fetch_page_html", fake_fetch)

    discovered = discover.scrape_all_links_with_retry(attempts=3, sleep_fn=lambda s: None)

    assert discovered == []
    assert calls["main"] == 3                     # used every attempt, no more


def test_scrape_all_links_with_retry_first_pass_ok_no_retry_needed(monkeypatch):
    """The common case: the main page has links on the first pass — no
    retry, no sleep."""
    calls = {"main": 0}
    sleeps = []

    def fake_fetch(url=discover.config.SOURCE_PAGE):
        if url == discover.config.SOURCE_PAGE:
            calls["main"] += 1
            return MAIN_PAGE_HTML
        raise RuntimeError("404 (sub-page not published yet)")

    monkeypatch.setattr(discover, "fetch_page_html", fake_fetch)

    discovered = discover.scrape_all_links_with_retry(attempts=3, sleep_fn=sleeps.append)

    assert calls["main"] == 1
    assert len(discovered) == 1
    assert sleeps == []
