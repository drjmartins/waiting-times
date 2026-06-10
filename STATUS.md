# Status

At-a-glance project state. For the full decision history see `DECISIONS.md`.

_Last updated: 2026-06-10 (Claude Code session)._

## Deployed and live ✅

- **Live site:** https://drjmartins.github.io/cancer-waiting-times/
- **Repo:** https://github.com/drjmartins/cancer-waiting-times (public)
- **Deploy:** GitHub Pages via `.github/workflows/update-data.yml` (daily cron
  `0 16 * * *` + manual `workflow_dispatch`). Build runs tests → fetches any new
  NHS files → rebuilds `site/data` → commits data back → deploys the Pages
  artefact. Source is genuine NHS England CWT data (OGL v3.0), 2022-23 → 2025-26.

### Verified on the first watched deploy (all four checks)
1. Actions run green and the Pages site loads (200s across pages + data).
2. The checkout-without-`data/raw` re-fetch path works (forced re-fetch of the
   2022-23 CSV from a clean runner, then committed manifest+store back).
3. Download slices resolve on the live site (per-FY CSVs, all-cancers headline
   extract, gzipped full file). `downloads/` is artefact-only (gitignored,
   rebuilt every run into the Pages artefact).
4. Daily cron registered; the no-op path rebuilds + deploys cleanly.

### Operational note
- **Expect a daily commit.** `meta.json` carries a `built_at` timestamp that
  changes every build, so each scheduled run makes a one-line "Auto update CWT
  data" commit even when no NHS data changed. It is the footer's "last updated"
  date — harmless, but the history will show a commit per day.

## Open threads (handed to planning / research)

1. **Overdispersion ↔ study-protocol alignment (research side).** The funnel uses
   Winsorised multiplicative φ (after Spiegelhalter), adjusted-by-default with an
   unadjusted toggle. This is a methods choice for the *underlying study protocol*,
   not just the dashboard — the two should use the same convention (multiplicative
   vs additive random-effects, Winsorisation fraction, whether to adjust at all).
   Needs a decision from the research side so dashboard and protocol stay aligned.
2. **Front-end / UX (planning session).** Two items: (a) the **download UI** — what
   slices to surface and how to label them (files are produced; the UI is unbuilt);
   and (b) a **"compare this trust" link** from the per-org page through to the
   comparison view scoped to that trust. Both are planning-session calls.

## Known things to keep an eye on
- **NHS "provider flat files" decommissioned 11 Jun 2026 — WATCH the first run
  on/after that date.** Pre-deploy check (10 Jun) confirmed the pipeline pulls
  the SURVIVING source (Combined Provider+Commissioner ICB-based CSVs); discover
  finds exactly the 5 combined links and normalise's column mapping holds against
  the live header. The decommission removes a different file set we never used.
  Residual: verified against the pre-decommission page — confirm the first
  scheduled/manual run after 11 Jun is green. See `DECISIONS.md`.
- FDS28 funnel has very high φ (~80) — verified not degenerate (15 trusts beyond
  95%, 4 beyond 99.8%), so adjustment isn't masking all outliers. Re-check if NHS
  data shifts. See `DECISIONS.md`.
- ICB as a comparator scope is deliberately deferred (trust↔ICB is many-to-many);
  needs an attribution convention from the study protocol before building.

## Running locally
```bash
pip install -r requirements.txt
python -m pipeline.run --synthetic   # offline dev (separate synthetic store)
python -m pipeline.run               # real run against NHS England
python -m http.server 8099 --directory site   # then open localhost:8099
python -m pytest -q                  # tests (also run in CI before deploy)
```
