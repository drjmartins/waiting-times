# Decisions log

Shared decisions across the two Claude sessions (Claude Code = pipeline/data/
infra/deploy; planning session = UX/audience/features/visual design). Newest
entries on top. Keep entries short (~3 lines): what, why, date, which session.

---

## 2026-06-10 — PRE-DEPLOY decommission check PASSED; pipeline pulls the SURVIVING source (Code)
The 11-Jun-2026 decommission targets the OLD "provider flat files" — NOT the
source this pipeline uses. Verified live against england.nhs.uk today:
 - The page's decommission notice reads: "we will be decommissioning the
   provider flat files below from 11th June 2026. The new format can be found
   under the Combined Provider and Commissioner (ICB based) section." That
   Combined (ICB-based) section IS exactly what discover.py scrapes.
 - discover.discover_csv_links() run against the LIVE page returns exactly the 5
   Combined CSVs (2022-23…2025-26, prov+final) and nothing else. There are only
   5 .csv anchors on the whole page — all combined — so there is ZERO risk of the
   marker ("Monthly Combined CSV") grabbing a decommissioned provider flat file.
 - normalise.py column mapping HOLDS against the live current combined header:
   all required fields resolve (Period/Basis/Org_Code/Org_Name/Standard_or_Item/
   Within/Total) and all three breakdown cols (Cancer_Type / Referral_Route_or_
   Stage / Treatment_Modality) + Parent_Org region are present.
 - Manifest is in steady state: select_files_to_process() = 0 to do; manifest's 5
   URLs match live.
Note: the combined files are ALREADY in their current ("new") format — that was
the Nov-2025 structural change this pipeline already handles; the decommission
only REMOVES the parallel provider flat files, it does not change the combined
layout. RESIDUAL: verified against today's (10 Jun) page; the change is tomorrow.
The notice says the combined section is unchanged, and normalise fails LOUDLY +
CI gates deploy if a field ever stops mapping, so a bad layout shift errors
rather than ships. RECOMMENDATION: watch the first scheduled run on/after 11 Jun
(or trigger one manually) to close this fully. Decommission does NOT block the
redesign deploy.

## 2026-06-10 — Per-org filtering feature: AGREED DIRECTION (single-dim + real pairwise combos, load-on-demand) (planning session, logged by Code)
Direction set after the breakdown-data investigation (full 3-way crossing is
impossible — source has no cancer×route×modality cells). The feature will be:
 - Single-dimension filters (cancer / route / modality) PLUS the specific NHS
   pairwise combinations where they actually exist — NOT an arbitrary Cartesian
   cross. Don't offer combos the source doesn't publish.
 - Filter UI RESHAPES per standard: FDS28 = cancer only (no route/modality);
   31-day & 62-day = fuller set (cancer, route, modality + their real pairwises).
 - Breakdowns LOAD ON DEMAND via a separate per-org breakdown file (e.g.
   org/<CODE>.breakdown.json, ~20-40KB gz) fetched only when a filter is opened;
   the lean 'all'-only file still drives first paint. THIS TOUCHES THE PIPELINE
   (build_site_data must emit the new file) — not pure front-end.
 - National comparison line matches the SELECTED slice (like-for-like): if the
   user filters to e.g. Breast | Surgery, the England overlay is that same slice.
 - Thin SUB-THRESHOLD months are shown but FLAGGED, not hidden (consistent with
   the funnel's reliability-threshold treatment).
NOT BUILDING YET — full spec to follow after the redesign renders are reviewed.

## 2026-06-10 — Per-org page v2 redesign built; PAUSED before deploy (Code, from planning spec)
Implemented per-org-redesign-spec_1.md in site/index.html — PURE FRONT-END, no
pipeline change (all needed fields — within_target, total, data_status — already
ship in the per-org/national JSON; nothing had to be flagged back). Changes:
(1) page DEFAULTS to National (national.json wrapped with name "England"), not
the first org alphabetically; (2) flat search picker replaced by a grouped
<select>: National pinned top, then Providers (201), then Commissioners (50),
alpha within group, grouping done client-side off index.json's level; (3) the
three small charts replaced by ONE large time-series chart + three summary cards
(FDS28/CMB31/CMB62) showing latest % + sparkline that DOUBLE AS THE STANDARD
SWITCHER (click a card → big chart switches, active card marked); (4) hover
tooltips anchored to each point: "Sep 2025 · 92.1% · 1,400 of 1,520 · final".
Big chart = org line (solid for finalised, dashed+lighter for the provisional
tail), faint dashed England overlay (suppressed when the org IS national), amber
target rule, y-axis auto-zoomed to data+target. Interaction per spec: switching
ORG keeps the selected standard (CURRENT_STD persists; only falls back if a std
is absent); switching STANDARD redraws only the chart. First load defaults to
CMB62 (most-watched). Added harmless deep-link params ?org=&std= (and ?tip=N for
deterministic tooltip renders). "Size of the prize" kept, now synced to the
selected standard. Renders: screenshots/perorg_v2_national.png (National default)
and perorg_v2_provider_cmb31_tip.png (RRK on CMB31 with tooltip). NOT DEPLOYED —
paused for planning review as usual.

## 2026-06-10 — INVESTIGATION (no build): per-org breakdown data for the planned cancer/route/modality filter (Code)
Scoping the follow-on per-org filter (cancer × route × modality). Two findings:
(Q1) CONFIRMED — the per-org JSON shipped to the front end carries ONLY the 'all'
slice. build_site_data._org_payload filters breakdown_type=='all'; national.json
same. The tidy store (data/processed/tidy.parquet, 1.147M rows) keeps everything:
all 27.8k / cancer 308k / route 48.6k / modality 68.6k / combination 694k. So the
breakdown rows exist upstream but are NOT in the site JSON today.
(Q2) Payload if a per-org file carried the full breakdown dimension: measured by
building it for real orgs — median provider ≈166KB raw / 22KB gz (~193 series),
largest ≈219KB raw / 37KB gz (~211 series), tiny orgs <1KB. ALL 201 providers =
23MB raw / 3.3MB gz. CONCLUSION: shipping every org's breakdowns up front (3.3MB
gz) is unreasonable and pointless (one org viewed at a time); but a single org's
breakdown file at 20–40KB gz is trivial to fetch on demand. Since the page already
loads one org JSON per selection, the natural design is LOAD-ON-DEMAND: keep the
lean 'all'-only file for fast first paint, add a separate per-org breakdown file
(e.g. org/<CODE>.breakdown.json) fetched only when a filter is opened. This DOES
need a small pipeline addition (emit the breakdown file) — not free front-end.
CRITICAL CAVEAT for the filter spec: the source does NOT support full 3-way
crossing. Every 'combination' row is at most PAIRWISE (665.9k of 666k are 2-part,
e.g. "Lung | Urgent Suspected Cancer"); there are ZERO cancer×route×modality
3-way cells. NHS publishes single dimensions + selected pairwise combos only. So
"fully crossable cancer AND route AND modality together" is NOT achievable from
this data — the spec should assume single-dimension filters + whatever specific
pairwise combos NHS ships, not an arbitrary Cartesian cross. (FDS28 also has no
route or modality at all — cancer only.)

## 2026-06-10 — DEPLOYED (first watched run); live at drjmartins.github.io/cancer-waiting-times (Code)
Public repo drjmartins/cancer-waiting-times, GitHub Pages via Actions. All four
post-deploy checks pass: (1) Actions run green and the Pages site loads (200 for
index/compare/data); (2) the checkout-without-data/raw RE-FETCH path works —
forced by dropping 2022-23 from the manifest, the hosted runner re-downloaded
the 53.4MB CSV fresh, normalised/merged, and committed the manifest+store back
(verified, data restored to 5 FYs); (3) download links resolve on the live site
(gz 10.4MB, headline 4.6MB, per-FY 57MB all 200) — the no-op-rebuild fix means
the gitignored downloads/ ship in the Pages artefact; (4) daily cron 0 16 UTC is
registered and the hosted no-op path rebuilds + deploys cleanly.
Gotchas surfaced by the first run (this is what first deploys are for):
 - GitHub did not index the workflow from the initial bulk push; touching the
   file in a follow-up commit forced registration.
 - 3 comparison tests passed on macOS but FAILED on Linux CI: they opened
   CMB62__all__All.json while the build writes lowercase slugs (..._all.json);
   macOS's case-insensitive FS hid it. Fixed by deriving the name via _slug.
   The tests-before-deploy gate caught it (nothing shipped on the red run).
 - Every run rewrites meta.json's built_at, so each daily run makes a one-line
   "Auto update CWT data" commit even with no data change (it is the footer's
   "last updated" date; harmless).

## 2026-06-10 — FDS28 high-phi funnel VERIFIED not degenerate (Code)
Eyeballed as flagged: FDS28 all-cancers phi=79.9 (very high — genuine large
between-trust variation in FDS reporting; FDS denominators are big, up to ~22k).
Limits flare very wide at low n but converge at high n, and a sensible handful of
high-volume trusts still breach: 15 beyond 95%, 4 beyond 99.8% of 140 clearing.
So the adjustment is not so strong that nothing is ever flagged (the opposite
failure to the 71/139 over-flagging). No change needed.

## 2026-06-10 — run_real always rebuilds the site, even on a no-op fetch (Code)
Deploy-blocking bug found before first deploy: run_real() early-returned before
build() when no new files were found, but the download slices and comparison
JSONs are build artefacts that are .gitignore'd (not in the CI checkout). So any
scheduled run with nothing new would upload a Pages artefact missing site/data/
downloads/ and refreshed compare/ -> 404s on the live site. Fixed: fetch is
conditional, but build() always runs from the current store (skipped only if the
store is empty). Verified locally: deleting downloads/ then running a no-op fetch
regenerates them. KNOWN-TO-VERIFY on the hosted run: that the artefact actually
ships downloads/ (check #3).

## 2026-06-10 — FDS28 funnel has very high phi (~80) — eyeball it (Code, non-blocking)
FDS28 all-cancers overdispersion phi is ~80 (vs 15 for CMB62, 4 for Lung),
plausibly real (FDS reporting varies hugely between trusts) but worth confirming
the limits aren't so wide that nothing is ever flagged — the opposite failure to
the 71-of-139 over-flagging we just fixed. 62-day and Lung look well-calibrated.
TO VERIFY: render FDS28 all-cancers adjusted funnel and check a sensible number
of genuine outliers still surface.

## 2026-06-10 — Funnel limits are overdispersion-ADJUSTED by default (Spiegelhalter); unadjusted via toggle (planning session + Code)
The default funnel was showing plain BINOMIAL limits everywhere — and the same
formula in every scope (the earlier "headline tight vs South West flaring" was a
denominator-RANGE artefact, not adjusted-vs-unadjusted; nothing was adjusted).
Fixed: limits now include a Winsorised multiplicative overdispersion factor phi
(after Spiegelhalter), computed at build time per measure, applied by default;
an unadjusted (binomial) view remains via the control. phi is estimated from
threshold-clearing units only (a 0.5-patient unit must not set dispersion) and
Winsorised at the 10th/90th percentiles so a few extreme trusts don't blow it up;
floored at 1.0. Effect on 99.8% breaches: CMB62 all-cancers 71->3 (phi=15.0),
CMB31 89->10 (phi=23), FDS28 104->4 (phi=80), Lung 25->2 (phi=4). A default funnel
flagging half the trusts had failed at its job; this restores it.
FLAG TO RESEARCH SIDE: the overdispersion choice (multiplicative Winsorised phi
vs additive random-effects, the Winsorisation fraction, whether to adjust at all)
is a METHODS decision for the underlying study protocol, not just the dashboard —
dashboard and protocol should use the same convention. Raising for alignment.

## 2026-06-10 — Funnel point encoding is non-judgemental (Code)
Replaced the red/amber/teal (bad/warn/good) point colours, which mislabelled
HIGH-performing outliers as failures and undercut the "position is not goodness,
not a league table" framing. New encoding: single neutral hue for all points;
FILL = direction (filled below the England line, hollow above); SIZE/emphasis =
how far beyond the limits (within < beyond-95% < beyond-99.8%). A high and a low
outlier now look equally noteworthy but visibly different in direction, neither
coloured 'bad'. Bonus: colour-blind safe. Sub-threshold = muted hollow grey ring
(funnel only); rest-of-England = faint grey. y-axis stays auto-zoomed to the
data with bounds labelled.

## 2026-06-10 — NHS small-number rounding leaves fractional values (0.5); don't truncate (Code)
Found during verification: 137,748 store rows (12%) carry fractional within/total
(min 0.5) from NHS small-number rounding. The comparison precompute was int()-
truncating, turning 0.5 -> 0, which injected 11 bogus zero-denominator "trusts"
(Ramsay, Spire, HCA…) with nonsense 1.0/0.0 performance into the headline and
div-by-zero'd the dispersion calc. Fixed: _num() keeps fractional values truthful
(0.5 stays 0.5, whole counts stay int); dispersion uses threshold-clearing units
only; the funnel limit() guards n<=0. These tiny units are sub-threshold anyway
(funnel-only). NOTE: the per-org page still int-casts its time series — cosmetic,
tiny months, left for a later pass.

## 2026-06-10 — Corrected live-tool footer/methods copy applied; "synthetic" footer removed (planning session copy, applied by Code)
index.html no longer claims "synthetic data … must not be used" (was false and a
deploy-blocker). Both pages now carry the live-tool-copy.md short footer, with
{latest_month}/{build_date} filled client-side from meta.json so they never go
stale. The comparison methods notes use the copy's overdispersion explanation
(which assumes adjusted-by-default — now consistent with the code).

## 2026-06-09 — Comparison basis = rolling 3 most-recent FINALISED months, pooled (planning session, logged by Code)
Default comparison period is the most recent 3 FINALISED months (currently
Jul–Sep 2025), NOT the single most-recent-final month. Rationale: a 3-month
aggregate stabilises the denominator exactly where the threshold/fallback bite
(granular breakdowns), is more current in spirit than one ~8-month-old month
(pools the freshest STABLE data), and finalised-only means the comparison
doesn't shift under users as provisional data revises (provisional months still
appear in per-trust time series, just not as the comparison basis). AGGREGATION
(hold firm): sum numerators and sum denominators across the 3 months, then
compute performance from the totals — never average three monthly percentages
(mis-weights months of different sizes). Exact months stated on screen
("Jul–Sep 2025, finalised"). config: COMPARISON_WINDOW_MONTHS=3. No period
selector built for v1 (the robust default is what matters); the precompute keys
off finalised months so a selector is a cheap later add.

## 2026-06-09 — Comparison precompute at build time; region scoping is a client filter (Claude Code)
Precompute one JSON per measure (standard x all/cancer/route/modality) at build
time rather than computing client-side over 1.1M rows — cleaner given the
breakdown combinatorics. Each file ships the national p0, z-values (1.96/3.09)
and threshold; the front end draws the funnel limit curves and does scope
filtering + fallback. Because limits are NATIONAL-anchored, one file serves every
scope (region = a client-side filter on the trust list), so no per-region
duplication. 61 measures, ~1.2MB total, committed. Combination breakdowns stay in
the store but are NOT offered as comparison measures in v1.
OBSERVATION for planning/methods: with plain binomial 95%/99.8% limits (as the
spec/protocol specify), ~71 of 139 trusts breach the 99.8% limit on the CMB62
all-cancers headline. This is expected funnel OVERDISPERSION on NHS provider data
(real between-trust variation exceeds binomial). I followed the spec exactly and
did NOT add an overdispersion adjustment (Spiegelhalter additive/multiplicative)
— flagging it as a methods question if the high breach rate reads as alarming.

## 2026-06-09 — Download slices replace the 200MB single CSV; downloads/ is artefact-only (Claude Code)
build_site_data._build_downloads emits per-financial-year CSVs (cwt_tidy_<FY>.csv,
~47–59MB each), an all-cancers headline extract (cwt_headline_all_cancers.csv,
~4.4MB) and the gzipped full file (cwt_tidy_full.csv.gz, ~10MB, was ~200MB raw),
plus a downloads/index.json manifest. The whole site/data/downloads/ dir is
.gitignore'd (rebuilt each run into the Pages artefact, like the old CSV) since
the per-FY files exceed sensible git sizes. The front-end download UI is the
planning session's to design — files are provided.

## 2026-06-09 — FLAG: index.html footer still says "synthetic, must not be used" (Claude Code)
The per-org page footer reads "Prototype built on synthetic data … must not be
used for analysis." That is now FALSE — the site is built from genuine NHS data.
This is product wording (planning's call) but it is a MUST-FIX-BEFORE-DEPLOY: a
real-data dashboard that disclaims itself as synthetic is contradictory. Not
changed unilaterally; flagged for the planning session.

## 2026-06-09 — Comparison view v1 is REGIONS-ONLY; ICB deferred (planning session, logged by Code)
Trust comparison view compares trusts scoped to England or a single NHS region.
ICB is deliberately NOT a comparator scope in v1: trust↔region is clean and
one-to-one, trust↔ICB is many-to-many (commissioners) and needs an attribution
convention not yet settled. DEFERRED, do not build yet: (a) ICB as a comparator
scope — when added, reuse the main study protocol's trust→ICB attribution so
dashboard and research stay aligned; ICB data stays in the store meanwhile;
(b) ranked league-table view (resisted to avoid league-table misreading);
(c) trailing-window smoothing if single-period proves noisy. Methods rules that
must hold: control limits anchored to the NATIONAL distribution (95%/99.8%),
denominator threshold reuses pipeline's ≥10, sub-threshold trusts appear in the
funnel only (not the percentile view), one-step region→England auto-fallback when
<5 threshold-clearing trusts, Oct-2023 comparability break applies. Full spec:
comparison-view-spec.md.

## 2026-06-09 — NHS region derives cleanly from Parent_Org; no ODS lookup needed (Claude Code)
Confirmed the regions-only rationale holds (this gated the build). `Parent_Org`
in the CWT file IS the NHS region: exactly the 7 England regions, one-to-one with
provider (0 of 201 providers map to >1 region across 4 FYs), zero blanks. So
region is captured directly in `normalise.py` (REGION_CANDIDATES -> Parent_Org),
added to the canonical schema and to index.json — no ODS organisation-reference
lookup required. Edge case: 2 providers (GEC 'Rapid Investigation Service',
S3H9L 'The Hamptons Hospital') carry Parent_Org='England' — genuinely region-less
national/independent providers; they belong to the England scope only, never a
single region. Not invented — that's their source attribution.

## 2026-06-09 — Placeholder orgs hidden from picker, retained in store/totals (Claude Code)
`build_site_data._is_placeholder` excludes the UNKNOWN unallocated-commissioner
bucket (and any name in PLACEHOLDER_NAMES) from index.json and per-org files, but
the 6,680 UNKNOWN rows stay in tidy.parquet and cwt_tidy.csv. Verified national
totals still reconcile (national CMB62 2025-09 = 30,483 = ICB-sum incl UNKNOWN's
174). Same keep-in-store / hide-from-selection pattern as the breakdown rows.
Picker now 251 selectable orgs (201 providers + 50 ICBs).

## 2026-06-09 — Checkpoint commit, date-format CI test, workflow validated (Claude Code)
Committed the clean real rebuild (252 orgs, 48 months, zero synthetic) as the
Git baseline; added `.gitignore`. Added `tests/test_normalise.py` pinning the
dual date-format behaviour (+ Total→national, Commissioner→icb, all-slice), wired
to run in CI before any fetch/deploy. Validated `update-data.yml` locally: YAML
parses, step order correct, incremental run is a clean no-op when nothing is new,
commit step respects `.gitignore`. NOT yet run on GitHub (no remote/Pages) — held
pending the comparison-view spec from the planning session. Deployment on hold.

## 2026-06-09 — cwt_tidy.csv (200MB) is artefact-only, never git-committed (Claude Code)
The full tidy download is ~200MB — over GitHub's 100MB file limit, so committing
it would make the workflow's `git push` fail. It is `.gitignore`d: rebuilt every
run into the `site/` Pages artefact (deployed) but never stored in git. NOTE for
planning session: serving/offering a 200MB CSV download is a UX/product question
(compress? per-year split? on-demand?) — flagging, not deciding.

## 2026-06-09 — Date format differs BY FILE VINTAGE; parse ISO-first w/ dayfirst fallback (Claude Code)
Correction to the entry below: a blanket `dayfirst=True` is WRONG. The 2025-26
files use DD/MM/YYYY (`01/10/2025`) but older files (≤2024-25) use ISO
`YYYY-MM-DD` (`2023-05-01`). dayfirst correctly parses the new files but misreads
ISO as year-day-month, collapsing every month in the three older files to
January (only 16 of 48 months survived, the rest silently mangled). Fix in
`normalise.py`: parse `format="%Y-%m-%d"` first, fall back to `dayfirst=True`
only for values that don't match. Lesson: NHS mixes date formats across vintages
— a date bug here fails silently, not loudly, so it must be checked explicitly.

## 2026-06-09 — Real and synthetic runs MUST use separate stores (Claude Code)
Found 1,596 fabricated rows merged into genuine NHS data (incl. the national ENG
line). Cause: `--synthetic` and real runs shared `data/processed/tidy.parquet`,
so a dev run seeded the next real run via `_load_store()`. Fix in `run.py`:
synthetic now writes `tidy_synthetic.parquet`; the real store is real-only.
Always check `source_file` has no synthetic rows after a real build.

## 2026-06-09 — Nov-2025 format change was STRUCTURAL, not a header rename (Claude Code)
The real Combined (ICB-based) CSV needed more than new `COLUMN_CANDIDATES`
entries. Structural changes handled in `normalise.py`: (1) breakdown is no
longer one (type,value) pair but three columns (Cancer_Type / Referral_Route_or_
Stage / Treatment_Modality) — now DERIVED into breakdown_type/value, retaining
every row (all/cancer/route/modality/combination); (2) no explicit org level —
basis is Provider/Commissioner and the all-England total is a pseudo-org
`Org_Code='Total'` — org_level now derived (Provider→provider, Commissioner→icb,
Total→national/ENG/England); (3) the period date format (see entry above).
Verified the 'Total' pseudo-org equals the exact sum of all providers before
trusting it as the national line; 62-day national lands high-60s/low-70s (real).

## 2026-06-09 — Retain breakdown rows in the tidy store; narrow only at site build (Claude Code)
`normalise.py` keeps ALL breakdown rows (cancer/route/modality/combination) in
`data/processed/tidy.parquet` and `site/data/cwt_tidy.csv`. `build_site_data.py`
consumes only `breakdown_type=='all'` for per-org JSON. Why: the three-column
breakdown is the raw material for future by-cancer-type / by-modality views;
keeping it now costs almost nothing, dropping at parse time means reprocessing.

---

## Pre-existing decisions baked into the codebase (seeded 2026-06-09)

- **Static-site architecture (no backend).** Data changes monthly, so a build-
  time Python pipeline feeding static files is cheaper/faster/safer than a live
  server. Deployed to GitHub Pages via daily GitHub Actions.
- **October 2023 comparability break is explicit in the UI.** 31-day and 62-day
  standards changed then; pre-2023-10 figures are not spliced into a continuous
  series — the UI defaults to 2023-10+ and labels the discontinuity.
- **Provisional→final revisions rule.** For the same period/org/standard/
  breakdown key, the newest data wins and `final` always beats `provisional`
  (`merge_with_revisions`).
- **"Size of the prize" = arithmetic gap only (v1).** Shows extra patients per
  month at a chosen target, explicitly NOT a modelled clinical/economic outcome;
  a caveated survival/economic module can be layered on later.
- **Format changes fail loudly.** `normalise.py` raises a named error when a
  required field can't be mapped, so CI catches the next NHS layout change.
