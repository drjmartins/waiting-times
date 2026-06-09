# Decisions log

Shared decisions across the two Claude sessions (Claude Code = pipeline/data/
infra/deploy; planning session = UX/audience/features/visual design). Newest
entries on top. Keep entries short (~3 lines): what, why, date, which session.

---

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
