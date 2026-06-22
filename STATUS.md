# Status

At-a-glance project state. For the full decision history see `DECISIONS.md`.

_Last updated: 2026-06-22 (Claude Code session; ODS org-status feature + RTT copy DEPLOYED + live-verified)._

## ✅ DEPLOYED + LIVE-VERIFIED 2026-06-22 (run 27948177203, build+deploy GREEN; CI commit aa3c52b)
- **Self-updating ODS org-status feature, BOTH dashboards** + **Part A RTT copy ×3** shipped together in one
  watched workflow_dispatch. Three lifecycle states (current / former-but-selectable / hidden) from ODS ORD
  succession links via shared `pipeline_common/ods.py` (FORMER = succession-link-passed, NOT Status); young
  orgs shown from month one; fail-soft to committed `ods_classification.json`. 50 tests pass.
- **Live checks (all explicit, headless + curl):** both dashboards 200; ODS fetch ran in CI for BOTH
  pipelines ("classified 416 orgs, 344 former, as_of 2026-05-07" — live path, not fallback); both RTT
  fail-loud gates intact (recon OK, TF-sum max|Δ|=0); QNQ/Frimley in Former group, selectable, 48mo history
  to Mar-2026, related-orgs note (→ S0E4D/S9B9J/QRL); Z9B2Z young, shown from its single Apr-2026 month, NOT
  hidden, "Formed" note; "Former organisations" picker group renders on each; Part A banner/footer/subtitle
  live with dynamic dates ("Data to April 2026. Last updated 22 June 2026"); un-hide-only confirmed
  (RTT 96→64, cancer 66→59, live_hidden ⊆ before_hidden, 0 wrongly-dropped); fail-soft re-confirmed
  (simulated outage → committed-cache fallback, no crash). Classification cache is a committed BUILD INPUT
  at repo root (not in the Pages artefact — it reaches users baked into index.json).
- Note: cancer data ends Mar-2026 (publication lag), so its 6 new ICB codes appear automatically when April
  CWT publishes; RTT already carries them. YOUNG_WINDOW_MONTHS=12 left simple per user (new IS clinics
  accepted as honest current providers).

## RTT dashboard (second dashboard, /rtt/) — increments 1 & 2 BUILT, NOT deployed ⏸
Parallel stack to the cancer one: `pipeline_rtt/` (config + build), `tests_rtt/` (9 tests),
`site/rtt/index.html` + `site/rtt/data/`. Source = the monthly RTT "Full CSV data file" (Incomplete
pathways, Part_2), 49 months Apr-2022→Apr-2026, NONC excluded, 6 metrics derived from the 105
wait-bands. 642 orgs (594 providers [96 hidden], 48 ICBs) + national. **TWO fail-loud gates pass**:
national vs Apr-2025 SPN (pct18 59.73%, waitlist 7.39M, w78/w104 exact, w52/w65 within 1%) AND the
TF-sum gate (24,776 org-months: sum of 23 TFs == C_999 total, max|Δ|=0). Front end reuses cancer
CSS/picker/range/expand/export/England mechanics; three cards = the measure toggle [% within 18wk ·
Waiting-list · Long waiters]; % chart = cancer CMB model + 65/70/92% lines; NEW count chart
(auto-scaling numeric axis); **treatment-function breakdown selector** (grouped Specialty/Other, 23
TFs) drives all three measures, with low-reliability (n<10) markers + matched England overlay + empty-TF
state; long-waiters [52·65·78·104] sub-control. Feb-2024 break marker+banner on all measures. 41 tests
pass (32 cancer + 9 RTT). **Functionally complete** (picker + 3 measures + 2 chart types + TF
breakdown + reuse mechanics). REMAINING: polish, deploy + CI/cron — awaiting the user. See DECISIONS.md
2026-06-19 (increments 1 & 2).

## Deployed and live ✅

- **Live site (post-restructure 2026-06-20):** https://drjmartins.github.io/waiting-times/
  — root landing → **/cancer/** (relocated Cancer dashboard + compare) and **/rtt/** (RTT dashboard).
  Old URL https://drjmartins.github.io/cancer-waiting-times/ now a stub repo doing a query/path-preserving
  redirect to …/waiting-times/cancer/.
- **Repo:** https://github.com/drjmartins/waiting-times (renamed from cancer-waiting-times; public)
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

### v7 — labelling/copy + data items + org-hiding — DEPLOYED ✅ (2026-06-12, run 27406241866)
Full set live + verified. Part 1: new title/subtitle, grouped provider/commissioner
pickers (Trust/ICB first; data classifies cleanly 173/28 + 42/8), byline prefixes
dropped, group helper text removed, Oct-2023 banner moved below the chart, redundant
third footer line removed. Part 2: Missing/Invalid excluded from "Other" (sentinel
EXCLUDED_GROUP; gap is FDS28-only ~0.28%, CMB31/CMB62 still exact; reconciliation
test one-directional); composite-group composition descriptions sourced from
cancer_groups -> meta.json (drift-guarded); Oct-2023 dashed "standards changed"
marker on CMB31/CMB62 charts only. Part 3: negligible-activity orgs hidden from the
picker, computed DYNAMICALLY each build, SELECTION-ONLY (files written, org in
store/downloads + reachable by ?org=) — commissioners with recent-3-month pooled
denom < 2000 (8 hubs). **v7.1 (same day):** provider rule TIGHTENED to a recent
window — hide if no standard clears n>=10 in a single month over the LAST 12 MONTHS
(config.PICKER_PROVIDER_WINDOW_MONTHS), catching dormant/defunct-merged codes that a
historical-only rule missed (now 58 providers hidden, 185 selectable); banner made
CMB31/CMB62-only (hidden on FDS28); banner's "defaults to 2023-10 onward" trailer
removed; footer gained a transparency note about the hiding. Live: CSH Surrey + the
dormant codes hidden, all reachable by ?org=. 32 tests pass.

### Chart-polish series (v8–v14) — ALL SHIPPED ✅ (2026-06-15)
A run of front-end-only (site/index.html, no pipeline/data change) visual passes on the
per-org page, deployed and verified live. v8/v9 (run 27547584946 / 27548485696): label/legend
tidy-up, "National"→"England", provider-dropdown layout fix, index gap fix, "Beta" relabels +
compare-page header. v10–v14 bundled into ONE deploy (run 27560316331, build+deploy GREEN,
verified live) — thirteen changes to the big breakdown chart + cards:
- **Title/hint:** group hint removed; chart title = `standard — cancer group` always (incl.
  All cancers); route/modality dropped from the title (read from the dropdowns).
- **Legend:** one line, organisation-only labels —
  "this organisation · low reliability (n<10) · provisional | England · target".
- **England line:** faint SOLID grey (dashed reserved for the org's own uncertain states) so
  it never collides with a provisional org line.
- **Annotations clear of data:** "standards changed" parked in a header strip (BG.P.t); the
  "target NN.N%" label moved into the right margin (BG.P.r).
- **Markers + precedence:** uncertain states shape-distinct — provisional = open circle +
  dashed, low-reliability (n<10) = open square + dotted — both in the SAME lighter teal, so
  shape+dash carry the distinction; final = strong solid teal + filled circle. Per-point state
  mutually exclusive, PROVISIONAL WINS (a both-states point renders provisional; square =
  final-but-low only).
- **Card sparklines:** brought in line with the chart's colour logic (lighter teal for
  provisional/low-n segments, strong solid teal for final); latest-point amber/teal target-cue
  dot deliberately kept (the at-a-glance "meeting target now?" signal).

### v15 — per-org chart: time-range + expand + image export — DEPLOYED ✅ (2026-06-16, run 27619479528)
Live + verified (build+deploy green; headless live render confirms 3y/12mo/All + FDS28 marker
behaviour). Three front-end-only additions to the per-org big chart (site/index.html), built to compose
(chart renders in the modal first, then export reads what's on screen, all respecting the range):
- **Time range** — fixed ROLLING window, segmented presets [3 years · 12 months · All],
  default 3 years (36mo), applied to ALL standards incl. FDS28. Clips the big chart's org +
  England series (cards' sparklines untouched). Adaptive x-axis labels (~8–10). The Oct-2023
  in-chart marker shows ONLY when the visible window includes pre-break data, and NEVER on
  FDS28 (verified clean in 3y/12mo/All); once the rolling window clears Oct-2023 (~2027) it
  drops out on its own, banner-below still carries the note.
- **Expand** — toolbar Expand button opens the chart in a fullscreen modal by MOVING the live
  panel into it (route/modality dropdowns, tooltips, export all keep working); ✕ / Esc /
  backdrop close. `?expand=open` hook.
- **Download** — PNG + SVG of a self-contained export (title + organisation + legend + the
  on-screen chart, CSS vars resolved, fonts inlined). Captures the on-screen slice AND window;
  filename + subtitle title-cased (e.g. Airedale-NHS-Foundation-Trust-CMB62-Haematology.png).

### v16 — per-org chart: show/hide England comparison line — DEPLOYED ✅ (2026-06-16, run 27620549350)
Live + verified (build+deploy green; headless live render confirms ON/OFF + England-tab behaviour).
A "Show England" checkbox in the chart filter row (default ON), providers + commissioners only.
OFF hides the grey England series, its legend entry and its pull on the y-scale (org series,
target, Oct-2023 marker, axis all stay); hidden on the England tab (the org's own line IS England
there). One switch — it gates ACTIVE_NAT in renderBig — so it carries into the expand modal and
the PNG/SVG export, and composes with the time-range window. Persists across switches; deep-link
hook `?england=off`.

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
