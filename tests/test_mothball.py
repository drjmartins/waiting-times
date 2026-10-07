"""
Tests for the mothball publish path (2026-10-07): `pipeline.run --no-fetch` and the
`updates_paused` stamp.

The scheduled cron is disabled because NHS's CDN/WAF serves empty pages to GitHub
Actions' egress. The manual workflow run (skip_fetch, the default) must therefore:
  1. never contact NHS or ODS (any network call would hit the blocked path),
  2. still run every fail-loud gate (it shares `_gate_and_build` with the fetch path),
  3. keep `built_at` so the footer's "Last updated" names the data refresh, not the
     day it was re-deployed,
  4. refuse to publish an empty dashboard if the committed store is missing,
  5. stamp `updates_paused` so the pages show the note.
"""
import json

import pytest

from pipeline import config, discover, run
from pipeline_common import freeze_note, ods


def _boom(*a, **k):
    raise AssertionError("network was contacted on the --no-fetch path")


def test_run_offline_contacts_no_network_and_preserves_built_at(monkeypatch, tmp_path):
    meta_dir = tmp_path / "data"
    meta_dir.mkdir()
    (meta_dir / "meta.json").write_text(json.dumps({"built_at": "2026-09-15T19:31:41.486173Z"}))
    monkeypatch.setattr(config, "SITE_DATA_DIR", str(meta_dir))

    monkeypatch.setattr(run, "_load_store", lambda path=None: [1])     # any non-empty store
    cached = {"orgs": {}, "nhs_trust_codes": ["RXX"], "as_of": "2026-09-10"}
    monkeypatch.setattr(ods, "load", lambda *a, **k: cached)
    seen = {}

    def fake_gate_and_build(store, ods_data=None):
        seen["ods_data"] = ods_data
        return {"built_at": "2026-10-07T12:00:00Z", "n_orgs": 3, "months": ["2026-06", "2026-07"]}

    monkeypatch.setattr(run, "_gate_and_build", fake_gate_and_build)
    # Any live fetch — NHS pages or ODS — must be unreachable from this path.
    for name in ("fetch_page_html", "scrape_all_links_with_retry", "scrape_all_links"):
        monkeypatch.setattr(discover, name, _boom)
    monkeypatch.setattr(ods, "refresh_or_cache", _boom)
    monkeypatch.setattr(ods, "refresh", _boom)

    run.run_offline()

    assert seen["ods_data"] is cached                       # committed ODS cache, not a live fetch
    written = json.loads((meta_dir / "meta.json").read_text())
    assert written["built_at"] == "2026-09-15T19:31:41.486173Z"   # data-refresh date kept
    assert written["n_orgs"] == 3                           # rest of the fresh meta is kept


def test_run_offline_refuses_a_missing_store(monkeypatch):
    monkeypatch.setattr(run, "_load_store", lambda path=None: None)
    with pytest.raises(RuntimeError, match="committed store"):
        run.run_offline()


def test_freeze_note_stamps_flag_and_keeps_the_rest(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    a.write_text(json.dumps({"built_at": "x", "months": ["2026-07"]}))
    b.write_text(json.dumps({"built_at": "y", "months": ["2026-07"], "n": 1}))

    freeze_note.stamp([str(a), str(b)])

    for p in (a, b):
        meta = json.loads(p.read_text())
        assert meta["updates_paused"] is True
        assert meta["months"] == ["2026-07"]                # nothing else disturbed
    assert json.loads(b.read_text())["n"] == 1


def test_freeze_note_refuses_to_stamp_when_a_meta_is_missing(tmp_path):
    a = tmp_path / "a.json"
    a.write_text(json.dumps({"built_at": "x"}))
    with pytest.raises(FileNotFoundError):
        freeze_note.stamp([str(a), str(tmp_path / "missing.json")])
