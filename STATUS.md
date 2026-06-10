# Status

At-a-glance project state. For the full decision history see `DECISIONS.md`.

_Last updated: 2026-06-10 (Claude Code session)._

## Deployed and live ✅

- **Live site:** https://drjmartins.github.io/cancer-waiting-times/
- **Repo:** https://github.com/drjmartins/cancer-waiting-times (public)
- **Deploy:** GitHub Pages via `.github/workflows/update-data.yml` (daily cron
  `0 16 * * *` + manual `workflow_dispatch`). Build runs tests → fetches any new
  NHS files → rebuilds `site/data` → commits data back (only when something other
  than `meta.json`'s timestamp changed) → deploys the Pages artefact. Source is
  genuine NHS England CWT data (OGL v3.0), 2022-23 → 2025-26.
- **CI hardening (2026-06-10):** actions pinned to Node 24-capable majors
  (checkout v6, setup-python v6, upload-pages-artifact v5, deploy-pages v5) ahead
  of the 16 Jun Node 20 removal; the commit step no longer makes a daily no-op
  "Auto update CWT data" commit (skips when only `meta.json` built_at changed).

### Per-org page — v2 → v4, all shipped & verified live
- **v2 redesign:** National default, grouped picker, ONE big time-series chart +
  three summary cards (latest % + sparkline) that switch the standard, hover
  tooltips, target-aware card cues.
- **v3 breakdown filtering:** load-on-demand per-org breakdown files
  (`org/<CODE>.breakdown.json` + `national.breakdown.json`, gitignored, rebuilt
  each run); single-dim + published pairwise slices (no Cartesian cross), UI
  reshapes per standard (FDS28 = cancer only), slice-matched national line,
  sub-threshold months shown-but-flagged.
- **v4 visual refinements (live as of run 27281517441):** (1) National/Providers/
  Commissioners type buttons + dependent dropdown (defaults to first org so the
  chart never blanks); (2) both org + breakdown dropdowns searchable (type-to-
  filter); (3) Size-of-the-prize follows the active standard — selector removed,
  slider kept; (4) legend shows marker dot + line matching the chart; (5) low-
  reliability (n<10) recoloured grey → muted org teal (`--org-muted`), distinct
  from the grey England line, still de-emphasised.

### Verified on the first watched deploy (all four checks) — still holding
1. Actions run green and the Pages site loads (200s across pages + data).
2. The checkout-without-`data/raw` re-fetch path works (clean-runner re-fetch +
   committed manifest+store back).
3. Download slices resolve on the live site (per-FY CSVs, headline extract,
   gzipped full file). `downloads/` + the breakdown files are artefact-only
   (gitignored, rebuilt every run into the Pages artefact).
4. Daily cron registered; the no-op path rebuilds + deploys cleanly (and, since
   the CI fix, without making a commit).

## Considered but NOT doing
- **Breakdown filter as a shared page-level control above the three cards.**
  Declined: available breakdowns differ by standard (FDS28 = cancer only; 31/62-
  day add route/modality + pairwise combos), so a single shared selector can't
  apply cleanly to all three at once. The breakdown filter stays on the big chart,
  scoped to the active standard. See `DECISIONS.md`.

## Open items
1. **11 June decommission verification — user to run on/after 11 Jun 2026.** The
   pre-deploy check confirmed the pipeline pulls the surviving Combined (ICB-based)
   source, not the decommissioned provider flat files. A copy-paste verification
   block (live discover + column-mapping + `gh run list`) was handed over; run it
   to close the residual. CI's fail-loud `normalise.py` + test gate protects the
   daily refresh meanwhile (a bad layout fails the run rather than shipping).
2. **NEXT TASK — data cleaning.** To be scoped in the planning session before any
   build. Not started.
3. **Parked.** (a) "Compare this trust" cross-link from the per-org page into the
   comparison view (planned, not built). (b) Overdispersion ↔ study-protocol
   alignment — a methods decision for the research side (multiplicative Winsorised
   φ vs additive random-effects, Winsorisation fraction, whether to adjust).

## Known things to keep an eye on
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
