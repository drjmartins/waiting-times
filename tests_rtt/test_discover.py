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
