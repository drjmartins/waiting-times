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

### Cancer-type aggregation (NHS's ten groups) + shared group filter (v5) — SHIPPED
- **PART A pipeline:** `pipeline/cancer_groups.py` rolls raw Cancer_Type labels into
  NHS England's ten tumour-site groups (sourced from NHS's own label hierarchy + CWT
  Monitoring Dataset Guidance v10.0; the only inferred mappings are the four
  FDS28-only sites with no dashboard group → Other). Added as a `cancer_group` dim in
  the per-org breakdown files ALONGSIDE the raw dims. Gate PASSED: the ten groups
  reconcile EXACTLY to the all-cancers total for all 27,816 org-month-standard cells
  across FDS28/CMB31/CMB62 (max |Δ|=0).
- **PART B front end:** shared searchable "Cancer group" selector above the three
  cards drives all three cards + big chart + size-of-the-prize together; persists
  across standard/org switches; default All cancers; muted-teal low-reliability
  (n<10) treatment on thin group sparklines + card caveat. Shared-group and
  big-chart granular filter are mutually-exclusive lenses (CONFIRMED at review).
- **Polish shipped same cycle:** Other-group cross-standard caveat (hint + tooltip);
  accurate "latest month, same rate as the card" basis label on the prize (the
  pooled-rate concern was a premise error — the per-org prize uses the latest single
  month and already matches the card; see `DECISIONS.md`). 25 tests pass.

### Item 1 — "Size of the prize" removed (2026-06-11) — DEPLOYED ✅
User wanted it gone, not hidden. Section + CSS + JS + call sites removed; no data
change (it read only core series fields). Deployed standalone (run 27339479076,
green) and verified live (zero prize refs).

### Items 2 & 3 — v6 context-aware breakdown dropdowns — DEPLOYED ✅
Group-aware **Referral route** dropdown + all-cancers-only **Treatment modality**
dropdown, built on the ≥1% activity bar (route characterisation showed routes are
partly cancer-specific — see `DECISIONS.md`). New `cancer_group_route` pipeline dim
(ten groups × route, composite groups aggregated, ≥1% per-org filter, fail-loud
reconciliation guard + store test). Front end uses a composite GROUP/ROUTE/MOD
state; spec's hide-and-reset transitions implemented. 30 tests pass; all 5 review
cases + transition + invalid-route reset rendered (screenshots/v6_a..f). Two
interpretation calls were accepted by the user as-is: raw cancer-subtype +
bare-modality breakdown options dropped (the ten-groups + route model is enough —
see deferred item below); FDS28 keeps its "no breakdowns published" line rather than
gaining a stage dropdown.

## Open items
1. **11 June decommission verification — user to run on/after 11 Jun 2026.** The
   pre-deploy check confirmed the pipeline pulls the surviving Combined (ICB-based)
   source, not the decommissioned provider flat files. A copy-paste verification
   block (live discover + column-mapping + `gh run list`) was handed over; run it
   to close the residual. CI's fail-loud `normalise.py` + test gate protects the
   daily refresh meanwhile (a bad layout fails the run rather than shipping).
2. **NEXT TASK — data cleaning.** To be scoped in the planning session before any
   build. Not started.
3. **Deferred (v6).** Cancer sub-type breakdown control. The v6 dropdown narrows
   cancer to NHS's ten groups (+ group-aware route); the finer raw cancer-subtype
   level (e.g. 'Haematological - Lymphoma') is no longer pickable in the UI. The
   data STILL RETAINS the sub-type level (the `cancer` dim in the breakdown files),
   so a sub-type control can be added later if anyone misses it — a deferral, not a
   data loss.
4. **Parked.** (a) "Compare this trust" cross-link from the per-org page into the
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
