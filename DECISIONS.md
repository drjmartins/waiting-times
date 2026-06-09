# Decisions log

Shared decisions across the two Claude sessions (Claude Code = pipeline/data/
infra/deploy; planning session = UX/audience/features/visual design). Newest
entries on top. Keep entries short (~3 lines): what, why, date, which session.

---

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
