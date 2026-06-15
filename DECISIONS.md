# Decisions log

Shared decisions across the two Claude sessions (Claude Code = pipeline/data/
infra/deploy; planning session = UX/audience/features/visual design). Newest
entries on top. Keep entries short (~3 lines): what, why, date, which session.

---

## 2026-06-15 — v8 VISUAL TIDY-UP: six label/legend changes + provider-dropdown layout fix; APPROVED & DEPLOYED (Code)
Front-end only (site/index.html), no pipeline/data change. 32 tests pass; JS node
--check clean. Six changes approved as-is; the two extra hints (FDS28 "breakdowns
aren't published" + group-selected "narrow by referral route") KEPT per the user
(informative, not redundant). Plus a follow-up layout fix (#7). Six changes:
1. "National" tab relabelled "England"; removed the "England · all-England aggregate"
   byline below the org selector (national byline now empty).
2. PROVIDER byline: dropped the bold provider name; kept the NHS region and moved it
   INLINE beside the dropdown (orgbtnwrap + orgname → inline-block; orgname now plain
   region text). Name still lives in the dropdown itself, so not lost.
3. COMMISSIONER byline: bold name dropped. ICBs all carry region "England", so the
   shared byline code renders NOTHING beside the dropdown for commissioners — exactly
   the "name removed, nothing else" the change asked for.
4. Chart subtitle (#bigtag): dropped the "CMB62 · target 85.0%" prefix (+ CMB31/FDS28
   equivalents) — now just the org name. Standard is in the chart title, target is on
   the chart's target line.
5. CMB31/62 only: removed the all-cancers route/modality helper strings ("Narrow by
   referral route, then treatment modality." and the route-selected follow-on "Pick a
   treatment modality to narrow this route further."). FDS28's own explanatory line and
   the GROUP-selected hint ("<group> group · narrow by referral route…") are KEPT (not
   named for removal) — flagged for confirm.
6. Legend: moved "provisional" to SECOND position (right after the org series); England
   comparison / target / low-reliability keep their relative order.
7. PROVIDER-DROPDOWN LAYOUT FIX (follow-up): the provider dropdown was flowing inline to
   the RIGHT of the type buttons (typebtns is inline-flex; orgbtnwrap was inline-block),
   making that row wide and pushing the region far right; the commissioner one only
   dropped below because its long ICB name wrapped. Wrapped the dropdown + inline region
   in a block .orgrow so it ALWAYS sits on its own line BELOW the buttons (mirrors the
   commissioner layout), with the NHS region staying inline to the right of the dropdown
   ON that lower row. National: orgrow holds the hidden dropdown + empty byline — no
   visible gap regression.
Renders: screenshots/v8_a_england (England tab, no aggregate line, subtitle "England",
legend org→provisional→target), v8_b_provider_region_inline (dropdown on its own row
below the buttons; region "North East and Yorkshire" inline to its right; subtitle = org
name only; no helper text), v8_c_commissioner (name gone, nothing beside dropdown),
v8_d_route_no_helper (Screening route selected — modality dropdown still appears, follow-on
helper text gone). DEPLOYED standalone & VERIFIED LIVE: run 27547584946 (workflow_
dispatch) — build + deploy both GREEN. Live: page 200; "England" tab present
(data-type=national → "England"); .orgrow wrapper present; removed strings gone
("all-England aggregate", the route/modality helper, ">National<").

## 2026-06-15 — INVESTIGATION (no change): why April 2026 is missing + FY-rollover detection risk (Code)
User noticed April 2026 is on the NHS site but the dashboard still shows "Data to
March 2026". Investigated live; nothing changed. THREE findings:

ITEM 1 — why April is missing (hypothesis was MOSTLY right, one correction). discover
finds exactly 5 Combined CSVs on the MAIN landing page (SOURCE_PAGE), latest = "2025-26
Oct–Mar Provisional" (data through March 2026); select_files_to_process = 0 to do. So
the dashboard correctly shows March 2026 given what's on the main page. CORRECTION to
the premise: April 2026 IS already in a Combined CSV — "April 2026 Monthly Combined CSV
Provisional" (…/2026/06/April-2026-Monthly-Combined-CSV-Provisional.csv) — but it lives
on the 2026-27 monthly SUB-PAGE, not the main page. The main page carries per-FINANCIAL-
YEAR CUMULATIVE Combined CSVs (2022-23…2025-26); the sub-pages carry PER-MONTH ones. The
pipeline consumes only the main page's per-FY cumulative files, and no 2026-27 cumulative
exists there yet. So April is reachable in a Combined CSV, just not via the page/granularity
the pipeline reads.

ITEM 2 — rollover detection (THE key one). NO hardcoded FY, fixed filename, or year list
in the code: _extract_financial_year is a generic (\d{4})-(\d{2}) regex; select_files_
to_process treats an unseen FY as "new financial year" and processes it. So when NHS adds
the "2026-27 Apr–… Monthly Combined CSV" to the MAIN page, discover will detect + ingest
it automatically (FY parses to "2026-27", new-FY → processed). The REAL risks are not a
year bug but two architectural assumptions, now concretely visible:
 (a) SINGLE-PAGE scrape — discover fetches only SOURCE_PAGE. We can SEE that NHS publishes
     the new-FY Combined CSV on the SUB-PAGE first (April's is there now, absent from the
     main page). The dashboard depends on the main page eventually carrying the 2026-27
     cumulative file; if NHS stopped maintaining per-FY cumulative files there, the pipeline
     would silently stall. TIMING: the 2025-26 main-page split (Apr–Sep / Oct–Mar half-year
     cumulative) suggests the first 2026-27 cumulative may not appear on the main page for
     months — so the dashboard can legitimately trail the latest per-month release for a
     while even with a perfectly working pipeline.
 (b) SILENT failure — a missed/late rollover is a GREEN no-op run (0 to process), not an
     error; nothing alarms that the latest data month has gone stale. That's exactly why
     this had to be caught by eye. There is no staleness heartbeat.
 Minor: marker match `m in clean` is CASE-SENSITIVE ("Monthly Combined CSV"); and the
 per-month sub-page label has no "YYYY-YY" token so _extract_financial_year returns
 "unknown" — both only bite if a fix starts consuming sub-page/per-month files (multiple
 "unknown" FYs would collapse in seen_by_fy). Not a problem for the expected main-page path.
 FIX DIRECTIONS (report only, not chosen): (i) also scrape the current-FY sub-page for the
 monthly Combined CSV (gets April now, but needs FY-parse + dedup work); (ii) add a
 staleness alarm (warn/fail if latest data month is > N months behind today) so a silent
 stall becomes loud; (iii) leave as-is and accept the main-page cumulative cadence. normalise
 still fails loud on any column change, so a layout shift in a new file errors rather than ships.

ITEM 3 — cron healthy. update-data.yml scheduled runs are firing daily and all GREEN
(6/6 recent scheduled, 12–14 Jun succeeded). NOT the suspect — corroborates item 1 (the
data simply isn't in a main-page Combined file yet). Committed manifest last_checked stays
2026-06-09 because it only advances when a new file is actually ingested (no-op runs don't
commit it) — expected, not a cron failure.

## 2026-06-15 — FOOTER tidy: source-line link + drop visibility note's last sentence; VERIFIED dynamic month (Code)
Front-end only (site/index.html footerHTML). VERIFICATION (asked): "Data to <month>"
is DYNAMIC, not hardcoded — latest=fullMonth(META.months[META.months.length-1]) (last
data month), built=isoDate(META.built_at); both advance automatically each refresh. No
fix needed. COPY: (1) made "NHS England Cancer Waiting Times statistics" in the FIRST
data-source line a link to the NHS CWT statistics page (target=_blank rel=noopener);
(2) REMOVED the visibility note's final sentence ("The complete Cancer Waiting Times
data … published by NHS England.", incl. its link added in the prior bundle) — note now
ends at "…very low recent total volume." Net: the NHS link moved from the visibility
note up to the source attribution, where it reads as the canonical-source pointer. 32
tests pass; JS node --check clean. Render: screenshots/footer_tidy (source link in line
1, note ends cleanly). DEPLOYED & VERIFIED LIVE: run 27544659015 (workflow_dispatch) —
build + deploy both GREEN. Live: page 200; first line carries the source-attribution
link (target=_blank rel=noopener) to the NHS CWT page; visibility note's trailing
"published by NHS England" sentence GONE; "Data to ${latest}" present as a runtime
template (month injected from META.months — dynamic, as verified).

## 2026-06-15 — COPY BUNDLE deployed: "Other" caveat + visibility-note reword (two copy changes, no logic) (Code)
Bundled the two held copy changes into one watched deploy (agreed: not worth a
standalone deploy for one-line copy). Source-only commit (code + this log); CI
rebuilds site/data from the committed store, so meta.json regains group_caveat on
the deploy build — local data-artefact churn (meta.json/compare) was reverted, not
committed.
CHANGE 1 — visibility footer note reworded (site/index.html footerHTML). Dropped the
"data is still in the dataset and downloads" claim (the /data/downloads/ static files
are NOT surfaced anywhere in the UI — no button/link; reachable only by direct URL —
so we don't promise them) and the "viewed via its direct link" sentence (not how
people access data, not actionable). Now ends: "The complete Cancer Waiting Times
data for all organisations is [published by NHS England]." linking (new tab,
rel=noopener) to england.nhs.uk/.../cancer-waiting-times/ (verified 200). INTENDED:
/data/downloads/ is no longer referenced in the UI — files still built, just not
surfaced; users directed to the authoritative NHS source. (Investigation behind the
reword: downloads = static per-FY CSVs + headline CSV + gzipped full file under
/data/downloads/, no UI; hidden orgs ARE genuinely in them — all 66 in the headline
CSV, confirmed live RVN/RWX/RRP — so the old claim was literally true but overstated
discoverability.)
CHANGE 2 — "Other" group caveat (the held change) ships: precise per-standard wording
in cancer_groups.OTHER_GROUP_NOTE -> meta.json.group_caveat.Other, driving both the
group hint and the 'Other' dropdown tooltip (see the BUILT entry below for detail).
32 tests pass; JS node --check clean. Renders: screenshots/footer_national (new NHS
link) + other_after_reword (Other caveat + new footer), both read correctly.
DEPLOYED & VERIFIED LIVE: run 27543685260 (workflow_dispatch) — build + deploy both
GREEN. Live (drjmartins.github.io/cancer-waiting-times): page 200; footer carries the
reworded note with the NHS link (target=_blank rel=noopener) and the NHS CWT page
resolves 200; old "still in the dataset and downloads"/"direct link" phrases GONE;
meta.json.group_caveat.Other present with the exact wording. As designed, CI's commit
step skipped (only meta.json built_at + the code-driven group_caveat changed, both
under the meta.json exclude) so git's committed meta.json stays without group_caveat —
the deployed Pages artefact is the freshly-built site/, which has it; every future
rebuild regenerates it from the committed code.

## 2026-06-15 — COPY: precise "Other" group caveat (no logic); BUILT, PAUSED before deploy (Code)
Replaced the imprecise "Other" caveat (old: "These sites appear only under the
28-day standard…" — wrong per the technical note: brain/CNS, sarcoma and children's
are inside CMB "Other (a)" too; only non-specific symptoms is FDS28-only) with the
exact reconciliation-friendly wording: "For the 28-day standard, NHS England
publishes data individually on brain/CNS, sarcoma, children's cancer, other cancers,
and non-specific symptoms, which are aggregated here. For the 31- and 62-day
standards, NHS England publishes a single 'Other (a)' line, covering the same cancers
except non-specific symptoms." SOURCED at the mapping (new cancer_groups.OTHER_GROUP_NOTE),
emitted into meta.json.group_caveat.Other, NOT hardcoded in the template — so it
travels with cancer_groups.py. Front end: dropped the two hardcoded JS constants
(OTHER_NOTE/OTHER_CAVEAT), added otherCaveat() reading meta; it now drives BOTH the
group hint AND the 'Other' dropdown tooltip (the tooltip carried the same old
imprecision — replaced too, so the two never disagree). "Other" no longer uses the
generic "Aggregates {comp}." template; the three other composites (Haem/Upper GI/
Urology) are unchanged. Applies to "Other" only. Rebuilt site from the existing real
store (185 orgs/48 months; group_caveat present). 32 tests pass; JS node --check
clean. Renders (Other selected, all three standards): screenshots/v7_q_other_caveat_
{fds28,cmb31,cmb62}.png — text reads correctly, wraps over two clean lines under the
group dropdown. NOT DEPLOYED — paused for review. Recommend bundling with the next
change rather than a standalone deploy for a one-line copy edit (your call).

## 2026-06-15 — REPORT ONLY: precise definition of the "Other" group per standard (Code)
Question for a writeup: what does "Other" measure under FDS28 / CMB31 / CMB62 —
NHS-published or dashboard-derived, and exact membership. Verified against the raw
Combined CSVs (distinct Cancer_Type per standard) + NHS England's authoritative
"Technical note on tumour classifications in 31 and 62 day combined standards"
(.xlsx, statistics/.../2023/12/, the doc the CWT stats page points to). FINDINGS:

PUBLISHED vs DERIVED:
 - CMB31 — NHS-PUBLISHED, 1:1. The source carries a single literal line "Other (a)";
   the dashboard group = that one line, no aggregation, no extra sites.
 - CMB62 — NHS-PUBLISHED, 1:1. Same literal "Other (a)" line, 1:1.
 - FDS28 — DASHBOARD-DERIVED. FDS28 has NO "Other (a)" line. The group is a residual
   bucket the rollup builds by summing FIVE separately-published "Suspected …" lines:
   "Suspected other cancer" + "Suspected brain/central nervous system tumours" +
   "Suspected sarcoma" + "Suspected children's cancer" + "Suspected cancer -
   non-specific symptoms". (Historically also "Missing or Invalid"; EXCLUDED since v7.)

LABEL: "Other (a)" is identical on CMB31 and CMB62; FDS28 has no such label (it uses
the "Suspected …" breakout instead). "(a)" is a footnote marker NHS attaches to every
residual line (also "Haematological - Other (a)", "Urological - Other (a)").

WHAT "(a)" DENOTES — exact NHS text (technical note, verbatim): «Other (a) are
defined as having ICD-10 codes that are classed as Brain/Central Nervous System,
Sarcoma, other cancers not separately classified, or children's cancers.» So CMB's
single "Other (a)" line ALREADY CONTAINS brain/CNS + sarcoma + children's + "not
separately classified" — NHS folds them in at source via ICD-10; CMB does not break
them out. (Same note: testicular → Urology, acute leukaemia → Haematology, confirming
those are NOT in Other.)

KEY UPSHOT (vindicates the by-elimination mapping, sharpens the cross-standard caveat):
the dashboard's four FDS28-only sites are NOT an arbitrary catch-all — brain/CNS,
sarcoma, children's, and "Suspected other cancer" (= "not separately classified") map
EXACTLY onto NHS's published ICD-10 definition of CMB "Other (a)". So FDS28 "Other"
reconstructs CMB "Other (a)" almost like-for-like, with ONE genuine divergence: FDS28
additionally absorbs "Suspected cancer - non-specific symptoms" (the NSS referral
pathway), an FDS-only concept with NO ICD-10 tumour equivalent and thus NO counterpart
in CMB "Other (a)". That single NSS line is the real reason cross-standard "Other" is
not a like-for-like cohort — not the brain/sarcoma/children's sites (those ARE in CMB
Other too). "Other (a)" is stable across the Oct-2023 comparability break (maps to
itself in both granularity vintages per the note). Nothing changed; report only.

## 2026-06-12 — v7.1 APPLIED & DEPLOYED (items 1–4) (Code)
User confirmed the LAST-12-MONTH window. Applied all four, deployed together (run
27423198402, green), verified LIVE (185 selectable; hidden {providers:58,
commissioners:8}; footer note present; banner trailer gone; AQK hidden but NQT /
Hamptons / Maidstone visible). (1) Oct-2023 banner now CMB31/CMB62-only, hidden on FDS28.
(2) PROVIDER hiding rule switched to "no standard clears n>=10 in a single month
within the last config.PICKER_PROVIDER_WINDOW_MONTHS (=12)" — selection-only +
dynamic, commissioner rule unchanged. Now hides 58 providers + 8 hubs (185
selectable): correctly adds the dormant/defunct codes (Vernova AQK, HCRG Care
Services NDA, and the merged Somerset RA4 / North Middlesex RAP / Mersey & West Lancs
RVY) WITHOUT the last-3 false positives (NQT HCRG Care Ltd n=150 and Hamptons S3H9L
n=468 stay visible — active within the year, just awaiting the latest provisional
months). (3) Footer transparency note added explaining the hiding (12-month provider
rule + low recent commissioner volume; data still in dataset/downloads; hidden orgs
reachable by direct link). (4) Trailing "This explorer defaults to data from 2023-10
onward." removed from the banner. 32 tests pass. Renders: v7_l/_m (banner FDS28 vs
CMB62), v7_n (dropdown scroll-to-selected), v7_o (trimmed banner + footer note), v7_p
(provider picker, tightened cut).

## 2026-06-12 — v7.1 amendments: items 1 & 3 BUILT; item 2 (tighter hiding) INVESTIGATED (Code)
ITEM 1 (built, front-end): the Oct-2023 comparability banner below the chart now
shows ONLY on CMB31/CMB62 and is HIDDEN on FDS28 (no break on the 28-day standard) —
toggled in renderBig (the single standard-change chokepoint). The in-chart marker was
already CMB31/CMB62-only. Renders: v7_l_fds28_no_banner, v7_m_cmb62_banner.
ITEM 3 (built, front-end): reopening the org dropdown on an already-selected org now
scrolls that option into view + leaves it highlighted (it already carried .active),
instead of starting at the top; focus(preventScroll) so the search box doesn't yank
the panel back up. Render: v7_n_dropdown_scroll_selected (Maidstone RWF mid-list,
scrolled-to + highlighted).
ITEM 2 (INVESTIGATED ONLY — report below; rule NOT changed, awaiting the user's
window choice). Some orgs survive v7's "never clears n>=10 in ANY standard/month"
because they cleared it once HISTORICALLY but are negligible NOW:
 - AQK Vernova CIC passes on a SINGLE point: FDS28 Apr-2022 n=114, never again
   (0 in the last 3 months, max 0.5 in the last 12).
 - NDA HCRG Care Services passes on CMB62 Jan/Nov-2023 (n=10.5/12.5); max 7 in the
   last 12 months, 4.5 in the last 3.
A RECENT-activity rule (hide if NO standard clears n>=10 within a trailing window),
framed by activity LEVEL (the n>=10 denominator bar), not literal point-count:
 - CURRENT all-time rule hides 53.  LAST-12-MONTH hides 58 (+5).  LAST-3-MONTH hides 60 (+7).
 - LAST-12 is the SAFE tightening. Clean gap: dormant orgs sit at <=9 in the last
   year, the next genuinely-active org (Walton Centre, a real small neuro trust) at 22.
   The +5 it adds are all genuinely dormant — AQK, NDA, and three trusts with large
   historical volume but ZERO in the last 12 months (Somerset RA4, North Middlesex
   RAP, Mersey & West Lancs RVY = defunct/merged codes). A full quiet YEAR is needed,
   so no single quiet quarter can trip it.
 - LAST-3 is UNSAFE: it wrongly hides TWO genuinely-active providers — NQT HCRG Care
   Ltd (n=150 within the last year) and S3H9L The Hamptons Hospital (n=468) — purely
   because the latest 3 PROVISIONAL months haven't populated yet (max_l3=0). This is
   the reporting-lag / quiet-quarter false-positive to avoid.
RECOMMENDATION: switch the provider rule to "no standard clears n>=10 in the last 12
months" (keep selection-only + dynamic; commissioner rule unchanged). Awaiting the
user's window pick; a follow-up applies it.

## 2026-06-12 — v7 FULL SET APPROVED & DEPLOYED (Code)
User reviewed + approved Parts 1 & 2 renders (all eight items right), then confirmed
the Part 3 hiding rules. Applied the hiding (below), removed the now-redundant third
footer line (Oct-2023 note duplicated the banner moved below the chart), re-rendered
(screenshots/v7_i provider picker, v7_j commissioner picker, v7_k CSH Surrey direct
link rendering with low-reliability flags), committed (7781201) + pushed, ran
update-data.yml (run 27406241866) — GREEN (tests + fetch/rebuild + deploy). Verified
LIVE: pages 200; title/subtitle updated; meta.group_composition present; 190
selectable, hidden {providers:53, commissioners:8}; CSH Surrey (NTV) hidden from the
picker but present in index.json (hidden=true) and reachable by ?org=NTV. The 53/8
counts held identically on CI's freshly-fetched data — the dynamic rule is stable.
ORG HIDING (Part 3) — applied, computed DYNAMICALLY each build (not a frozen list),
SELECTION-ONLY (files still written, org in store/downloads + reachable by ?org=):
 - providers hidden if they NEVER clear n>=10 in any standard/month (53; clean gap —
   hidden peak at 9/mo, next kept org 12.5); rule reuses RELIABILITY_THRESHOLD.
 - commissioners hidden if recent-3-finalised-month pooled all-cancers denom (summed
   across standards) < config.PICKER_MIN_COMMISSIONER_DENOM=2000 (the 8 commissioning
   hubs at <=869; smallest real ICB 11,737). index.json carries hidden=true; front
   end filters it from picker/default lists but resolves a direct ?org= against the
   full index.

## 2026-06-12 — v7 Parts 1 & 2 BUILT (labelling/copy + data items); Part 3 INVESTIGATED, not cut (Code, from v7-labelling-and-org-hiding-spec.md)
Built, tests green (32, +2), re-rendered, NOT deployed (paused for review as usual).

PART 1 — front-end labelling (site/index.html, pure front-end):
 - Title -> "NHS Cancer Waiting Times Dashboard" (h1 + <title>); subtitle ->
   "England · Performance against NHS Cancer Waiting Time Targets".
 - Provider picker GROUPED "NHS Trust" / "Other" (trusts first); commissioner
   picker grouped "ICB" / "Other" (ICBs first). Client-side classify off the org
   NAME, mirroring a pipeline rule. DATA CLASSIFIES CLEANLY (flag resolved): 173
   trusts vs 28 other providers (private/community/LLP), 42 ICBs vs 8 commissioning
   hubs — zero ambiguous cases. (Two trusts needed name-form handling: "NHS FT"
   abbrev + "NATIONAL HEALTH SERVICE TRUST" spelled out.)
 - Bylines: dropped the "Provider (trust)" / "Commissioner (ICB)" prefix — now
   name + region only (e.g. "AIREDALE NHS FOUNDATION TRUST · North East and Yorkshire").
 - Removed the "NHS England's ten tumour-site groups…" helper text by the group
   dropdown (the hint now shows composition / caveats only).
 - Moved the Oct-2023 comparability banner to BELOW the chart.

PART 2 — data items (pipeline + front-end):
 - EXCLUDE Missing/Invalid from "Other". cancer_groups: maps "Missing or Invalid"
   to a sentinel EXCLUDED_GROUP (not Other), so the rollup (iterates TEN_GROUPS)
   drops it; group_for stays exhaustive (new labels still fail loud). CONSEQUENCE
   confirmed-acceptable: ten groups no longer sum exactly to all-cancers — but the
   gap is FDS28-ONLY (Missing/Invalid is FDS28-only, ~0.28% of FDS activity; ZERO
   in CMB31/CMB62, which still reconcile exactly). Reconciliation TEST relaxed to
   one-directional: groups must never EXCEED the total (corrupting double-count
   direction, still exact) but may fall SHORT by exactly the Missing/Invalid count.
 - COMPOSITION description for composite groups only (Haematology, Upper GI,
   Urology, Other) — sourced from cancer_groups._COMPOSITION (labels tied to
   GROUP_OF via assert_composition_consistent(), a build-time drift guard) and
   emitted into meta.json.group_composition. Front-end shows "Aggregates …" in the
   group hint; the six 1:1 groups show nothing. Other shows its make-up + the
   cross-standard caveat, and (per item 9) does NOT list Missing/Invalid.
 - Oct-2023 vertical dashed "standards changed" marker on CMB31 + CMB62 charts
   only (read from meta.comparability_break); NOT on FDS28. Verified present on
   CMB31/CMB62, absent on FDS28.
 Renders: screenshots/v7_a..h (national; Airedale byline; Haematology + Upper GI
 composition; Other caveat; grouped provider dropdown; CMB31/CMB62 marker; FDS28
 no-marker).

PART 3 — org hiding: INVESTIGATED ONLY (reported below, no cut made). The data
separates cleanly but the right RULE DIFFERS BY ORG TYPE:
 - PROVIDERS: rule (a) "never clears n>=10 in any standard/month over 48 months"
   hides 53 of 201, and it coincides with a NATURAL GAP — the 53 hidden top out at
   max 9 patients/month; the next (kept) org jumps to 12.5+. These produce only
   empty/greyed charts (incl. CSH Surrey, the example). Clean, principled cut.
 - COMMISSIONERS: rule (a) hides ZERO (all 50 clear n>=10). But there's a ~10x
   activity gap: the 8 commissioning hubs (H&J + National) peak at max 287 / rec-3
   869, while the smallest REAL ICB starts at max 2822 / rec-3 11,737. A volume
   threshold (e.g. max single-month < ~1000, or recent-3 pooled < ~2000) isolates
   exactly those 8 — and they're the SAME 8 that fall in the picker's "Other" group.
 AWAITING the user's choice of rule per type; hiding will be SELECTION-ONLY (data
 stays in the store; org reachable by direct ?org= link). A follow-up applies it.

## 2026-06-11 — v6 APPROVED & DEPLOYED; both flags accepted (Code)
User approved the v6 build after reviewing the renders (Breast shows all four real
routes incl. Breast Symptomatic + Screening; Skin correctly omits both; modality
2nd dropdown, hide-reset transition, and FDS28 "no breakdowns" line all read well).
Both flagged interpretation calls accepted as-is:
1. Cancer SUB-TYPE granularity removal is fine — ten-groups + route is sufficient.
   Logged as a KNOWN DEFERRED ITEM (STATUS open item 3), NOT a loss: the `cancer`
   dim still carries the sub-type level in the breakdown files, so a sub-type
   control can be added later if anyone misses it.
2. FDS28 with no stage dropdown stays — the explanatory line handles it cleanly;
   not worth the extra build.

## 2026-06-11 — Items 2 & 3 BUILT (v6 context-aware breakdown dropdowns); built, then deployed (Code, from breakdown-hierarchy-v6-spec.md)
Built on the confirmed >=1% activity bar. Pipeline + front end done, 30 tests pass.

PIPELINE: new `cancer_group_route` dim in the breakdown files — ten groups x route,
built from the cancer x route combos, composite groups (Haem/Upper GI/Urology/Other)
aggregated by summing num+denom (same rollup as `cancer_group`). A (group, route)
slice is emitted only when its cumulative denom is >= 1% of the group's route
activity, PER ORG (so a small trust shows fewer routes). Verified: Breast keeps all
four routes incl. Breast Symptomatic; Skin/Urology drop Screening + Breast
Symptomatic; Lung/Lower GI keep Screening, drop Breast Symptomatic. FDS28 has no
route dim -> no cancer_group_route. Reconciliation: build-time fail-loud guard
catches the corrupting direction (routes EXCEEDING group total = double-count) so it
survives minimal unit fixtures; EXACT equality asserted as a store-level test
(routes partition the group total exactly, per org-group-month, max|delta|<0.6).

FRONT END: replaced the single freeform "Breakdown" dropdown with a composite
GROUP/ROUTE/MOD model + two controls — a group-aware **Referral route** dropdown
(all standards with routes; lists the group's real routes when a group is selected,
all-cancers routes otherwise) and a **Treatment modality** dropdown that appears
ONLY in all-cancers + CMB31/CMB62 + a route with a published modality level. Cards
follow the GROUP only; route/modality narrow the big chart. State transitions per
spec: selecting a group resets+hides modality (route kept iff valid for the new
group, else reset to All routes); returning to all-cancers reappears modality at
default; FDS28 shows neither control (hint explains). Searchable dropdowns + low-
reliability treatment preserved. Reviewed all 5 cases + transition pair + invalid-
route reset (screenshots/v6_a..f).

TWO INTERPRETATION CALLS FLAGGED FOR REVIEW (chose, did not guess silently):
1. The v6 dropdown is now ROUTE+MODALITY only. The old freeform breakdown let you
   pick a RAW cancer SUBTYPE (finer than the 10 groups, e.g. 'Haematological -
   Lymphoma') and a bare all-cancers modality / arbitrary combination. Those are
   GONE — cancer is the 10-group selector; modality is reachable only beneath a
   route. Matches the spec's "the breakdown dropdown becomes the route dropdown",
   but it removes sub-group cancer granularity. Restore a cancer-subtype control if
   that granularity is wanted.
2. FDS28 gets NO level-1 stage dropdown. The spec wanted FDS28 "referral-stage
   options", but FDS28 has no standalone route/stage dim — stages live only inside
   per-cancer combos (cancer x stage). Supporting FDS28 group->stage is doable
   (treat those combos as the route source, same activity bar) but wasn't in the 5
   review cases; left out for now. Confirm if you want FDS28 group->stage too.

## 2026-06-11 — Item 1 DEPLOYED (standalone): prize removal live & verified (Code)
Committed (778f73f) + pushed; ran update-data.yml via workflow_dispatch (run
27339479076) — green (tests + build + deploy). Live HTML at
https://drjmartins.github.io/cancer-waiting-times/ returns 200 with ZERO prize
references. Done.

## 2026-06-11 — CORRECTION to the breakdown-hierarchy investigation; v6 build PAUSED (Code)
User challenged my claim that "Breast Symptomatic" is a cancer-agnostic route. They
were RIGHT — I read cell EXISTENCE, not activity. Verified against real num/denom:
- **Routes are PARTLY cancer-specific.** "Lung | Breast Symptomatic" exists but is
  8 patients across 8 months (all sub-threshold) — miscoding noise, not a pathway.
- **CMB62 route applicability (summed denom; share of group; reliable months):**
  - *Breast Symptomatic* — BREAST ONLY (5,584; 2.8%; 48mo). Every other group
    0.0–0.1%, 0 reliable months. Breast-specific.
  - *Screening* — only the screening-programme cancers: Breast (35%), Lower GI
    (14%), Lung (4.7%), Gynaecology (3.5%). Trace/noise for Haematology (0.5%),
    Urology, zero for Head & Neck / Skin / Upper GI / Other.
  - *Consultant Upgrade* & *Urgent Suspected Cancer* — genuinely universal (all 10
    groups, 18–82%, 48+ reliable months).
- **CMB31:** First Treatment + Subsequent — both universal across all groups.
- **FDS28:** identical pattern, even cleaner (non-applicable cells are genuine
  ZEROS, not noise): Breast-Symptomatic-not-suspected = Breast only; National
  Screening Programme = Breast/Lower GI/Gynae/Lung(+Other); Urgent Suspected
  Cancer = all groups.
**Spec impact:** the v6 route dropdown must be driven by REAL per-(group,route)
activity, NOT a fixed route list — else it would offer e.g. "Breast Symptomatic"
under Lung (n=8) and "Screening" under Skin (n=0). Must filter PER ORG (per-org
files are sparser still). Build approach: emit a (group,route) slice only when it
clears an activity bar (mirrors the existing empty-cancer_group omission); front
end lists whatever slices are present. Proposed bar: ≥1% of the group's route
activity (cleanly keeps Breast-only Breast-Symptomatic + the 4 screening cancers,
drops the noise) — AWAITING user confirm before resuming the build.

## 2026-06-11 — Item 1 BUILT: "Size of the prize" removed from per-org page (Code)
User wants it gone (not hidden). Removed the whole `<section class="prize">`, its
CSS block (`.prize/.prizegrid/.slider/.result/...`), the JS (`prizeSeries/setupPrize/
recalc`), and all three call sites. No pipeline/data change needed: the prize read
only core series fields (target/performance/total/months) that the cards + chart
already use — nothing in the data build existed solely to feed it. Re-rendered
national page (screenshots/item1_prize_removed_national.png), no JS breakage.
NOT yet deployed — awaiting user confirm of the render; recommend a standalone
deploy since item 2 is investigate-only and item 3 is unspecced.

## 2026-06-11 — INVESTIGATION (no build): context-aware / two-level breakdown dropdown — feasibility from the data (Code)
User wants the breakdown dropdown to (a) filter to the SELECTED cancer group's
sub-breakdowns, and (b) add a SECOND dropdown for a further (modality) level.
Inspected the actual breakdown files. Findings:

- **Combination cells are PAIRWISE only — confirmed again, now classified.** Across
  every standard the `combination` dim contains exactly two shapes and NOTHING else:
  `cancer × route` and `route × modality`. There are ZERO `cancer × modality` cells
  and ZERO three-way `cancer × route × modality` cells. (CMB62: 82 combos = 66
  cancer×route + 16 route×modality. CMB31: 40 = 32 cancer×route + 8 route×modality.)

- **Level 1 → 2 (cancer group → route/stage) IS published.** Each cancer publishes
  cancer×route combos: CMB62 routes = {Breast Symptomatic, Consultant Upgrade,
  Screening, Urgent Suspected Cancer} (most cancers carry all four; a few rare ones
  carry a subset — e.g. Acute leukaemia/Testicular have only Consultant Upgrade +
  Urgent Suspected Cancer). CMB31 routes = {First Treatment, Subsequent} for every
  cancer. FDS28 has NO route/modality dims; its combos are cancer × referral STAGE
  (Urgent Suspected Cancer / National Screening Programme / Breast Symptomatic
  cancer-not-suspected) — so FDS28 supports level 1→2 but has NO second level.

- **The user's "sub-sub" (Breast Symptomatic → Anti-cancer drug regimen/Other/
  Radiotherapy/Surgery) is a CONFLATION.** "Breast Symptomatic" is a referral ROUTE
  (it pairs with EVERY cancer, incl. "Lung | Breast Symptomatic"), not the Breast
  cancer group. The modality split under it ("Breast Symptomatic | Surgery" etc.)
  exists ONLY as a route×modality slice that is ALL-CANCERS — never scoped to a
  cancer group. So the modality level is publishable as a standalone route→modality
  drilldown, but NOT as cancer-group → route → modality. The latter is the forbidden
  three-way (zero cells). So the literal two-level-under-a-selected-group design is
  NOT achievable for the modality level; only the route level can be group-aware.

- **Hierarchy differs by standard:** CMB31/CMB62 = cancer→route (+ all-cancers
  route→modality available, but un-nestable under a group). FDS28 = cancer→stage,
  no modality, so no second level there. So the second dropdown can only ever appear
  for CMB31/CMB62 and only in an all-cancers route→modality context.

- **Data readiness:** group→route is NOT yet directly in the files. The cancer×route
  combos are keyed on the 18 RAW cancer labels, but the front-end's selector uses the
  10 ROLLUP groups. The 1:1 groups (Breast, Gynaecology, Head & Neck, Lower GI, Lung,
  Skin) could read a single raw combo, but the COMPOSITE groups (Haematology = 4–5
  raw labels; Upper GI = 3; Urology = 4; Other = catch-all) need their raw cancer×route
  combos AGGREGATED (sum numerator+denominator across members, same reconciliation
  pattern as the existing cancer_group rollup). That is a PIPELINE change: precompute
  a `cancer_group × route` combination. route×modality (all-cancers) is already in the
  files as-is. Conclusion: feasible but needs a pipeline step for group-aware routes;
  the modality second level cannot be made group-aware at all.

## 2026-06-10 — Cancer-type aggregation into NHS's ten groups + shared group filter; BUILT, PAUSED before deploy (Code, from cancer-aggregation-v5-spec.md)
REVISITS the idea declined below: a shared breakdown filter above the three cards.
Now viable because we aggregate raw cancer types into NHS England's ten tumour-site
groups (Breast, Gynaecology, Haematology, Head & Neck, Lower GI, Lung, Other, Skin,
Upper GI, Urology) that exist across ALL three standards, so one selector applies
consistently. PART A (pipeline): new pipeline/cancer_groups.py — canonical raw-label
-> group lookup, EXHAUSTIVE (group_for raises on any unmapped value; tests assert
every store label maps). MAPPING SOURCE: NHS England's OWN published labels in the
Combined CWT file already encode the hierarchy — CMB31/CMB62 top-level labels ARE the
group names; sub-breakdowns are parent-prefixed ('Haematological - Lymphoma' -> Haem,
'Urological - Prostate' -> Urology); CMB62 splits the "rare cancers" (acute leukaemia,
testicular) out and the CWT Monitoring Dataset Guidance v10.0 §5.5/§6 names acute
leukaemia as a haematological malignancy + testicular under urology, so they roll
back. NOT improvised. The FOUR FDS28-only labels with no dashboard group (brain/CNS,
sarcoma, children's, non-specific symptoms) + 'Missing or Invalid' map to Other BY
ELIMINATION (NHS's ten-group CMB reporting has no line for them, so they sit in CMB
"Other") — the only inferred (not label-read) assignments; FLAGGED here and in the
report. Aggregation SUMS numerators + denominators per (month,org,standard,group)
then computes performance (never averages %). Built as a new 'cancer_group' dim in
_breakdown_payload ALONGSIDE the raw cancer/route/modality dims (not a replacement);
+~3-4KB gz/org, load-on-demand as before. VALIDATION (the gate): all ten groups
construct in FDS28 AND CMB31 AND CMB62; parent+child NEVER co-occur in a cell (so
summing can't double-count; a build-time + test guard fails loudly if a future NHS
vintage breaks that); RECONCILIATION is EXACT — the ten groups' summed denominators
(and numerators) equal the all-cancers headline for all 27,816 (month,org,standard)
cells, max |Δ| = 0.00, across all three standards. No group failed → Part B was
cleared. PART B (front end, site/index.html): a shared "Cancer group" searchable
dropdown ABOVE the three cards (All cancers default + the ten groups). Modelled as a
'cancer_group' slice in the SINGLE CURRENT_SLICE state, so the shared group and the
big-chart granular filter are MUTUALLY-EXCLUSIVE lenses (the chart is never out of
sync with a selector). The group PERSISTS across standard + org switches (only a
group slice survives a switch; granular slices reset to All, as before) — picking a
granular slice supersedes the group (cards revert to All). Cards + sparklines + big
chart + size-of-the-prize all follow the group together. Thin group series get the
existing muted-teal/dashed low-reliability treatment (n<10) on the sparklines (+ a
"n=…, low reliability" caveat and a de-emphasised latest figure) and on the big chart.
DECISION TO CONFIRM AT PLANNING (spec point B4): I made the shared group and the
big-chart granular filter mutually-exclusive (one lens at a time) rather than nesting
granular within the group — cleanest, never incoherent, but the spec flagged this as
a "bring to planning if fiddly" call. Renders: v5_a_all_national (All default),
v5_b_lung_national (Lung — all three cards + chart + prize updated), v5_c_groupopen
(searchable group dropdown), v5_d_thin_barts (Barts Head&Neck CMB62 — muted-teal thin
sparkline + card caveat + big-chart treatment), v5_e_thin_tip. 25 tests pass (was 16;
+9). JS node-parse clean. NOT DEPLOYED — paused for planning review.
CAVEAT noted: the "Other" group's COMPOSITION differs by standard (FDS28's Other also
absorbs brain/CNS/sarcoma/children's/NSS, which have no dashboard group); each
standard still reconciles to its own all-cancers total, so the filter is sound, but
cross-standard "Other" is not a like-for-like cohort.
REVIEW OUTCOME (planning, 2026-06-10): APPROVED. Mutually-exclusive group/granular
lenses CONFIRMED as the right call (keep it). v5 first deployed green (run
27310060320). Two MINOR polish items then FOLDED IN and shipped in a second watched
run:
 (1) DONE — "Other" group: grouphint now shows a caveat when Other is selected
     (FDS28's Other also absorbs brain/CNS, sarcoma, children's, NSS — not a
     like-for-like cohort across standards) + a hover tooltip on the Other option.
 (2) Re-scoped after checking the code: the request assumed the per-org prize uses a
     rolling 3-month POOLED rate (and that the Barts H&N "84%" contradicted the card's
     50%). It does NOT — the per-org prize uses the LATEST SINGLE month, and after the
     prize-follows-group fix it already MATCHES the card (both 50.0%); the 84.1% was
     the ALL-CANCERS figure, i.e. pre-fix behaviour. (Rolling-3-month pooling is the
     COMPARISON view, not this prize.) So a "pooled rate" label would be FALSE. Shipped
     an ACCURATE basis label instead: "Based on the latest month (…) — the same rate
     shown on the card above[, for the <group> group]", plus a thin-month volatility
     warning when n<10. Renders: v5_f_other_note, v5_g_thin_prizebasis, v5_h_other_open.
     RESOLVED (planning, 2026-06-10): keep the per-org prize on LATEST-MONTH basis —
     it matches the card, and thin-group fragility is handled by the low-reliability
     flag (the n<10 caveat + volatility warning), NOT by smoothing/pooling. No further
     change. Both polish items shipped + live (run 27310406923, green; verified on the
     live site). v5 fully DEPLOYED.

## 2026-06-10 — DECLINED: breakdown filter as a shared page-level control above the cards (planning session + Code)
Considered moving the breakdown filter above the three summary cards as a single
shared, page-level selector applying to all standards at once. NOT doing it: the
available breakdown dimensions differ BY STANDARD (FDS28 = cancer only; 31-day /
62-day add route, modality + published pairwise combos), so one shared selector
can't apply cleanly across all three — it would offer slices that don't exist for
FDS28. The breakdown filter STAYS on the big chart, scoped to the active standard
(reshaping as the standard changes). Cards + size-of-the-prize remain all-cancers.

## 2026-06-10 — Per-org page visual refinements (v4) SHIPPED + verified live (Code, from per-org-visual-v4-spec.md)
Front-end only (site/index.html), no pipeline/data change. Five changes:
(1) ORG SELECTOR replaced by three type buttons (National | Providers |
Commissioners) + a dependent dropdown below. National hides the dropdown (it's
just England); Providers/Commissioners show it and DEFAULT to the first org
alphabetically so the chart never goes blank. Default load stays National. Active
button marked. (2) Both dropdowns (org + breakdown) are now custom in-DOM
dropdowns with a type-to-filter SEARCH box (substring on name/code for orgs;
across all dim values for breakdowns); Enter picks the first match, Esc closes,
click still works. The native <select> org picker is gone (native selects can't
substring-filter). (3) SIZE-OF-THE-PRIZE standard selector REMOVED; the panel now
follows the active standard (cards + chart + prize all switch together via the
card click), shows a "Standard: … · CMBxx" readout, keeps the target slider, stays
all-cancers. (4) LEGEND entries now render a marker dot + line in each series'
exact style (England comparison + target have no dot, matching the chart; org,
provisional, low-reliability do). (5) LOW-RELIABILITY (n<10) markers + dashed
segments recoloured grey -> MUTED/lighter org teal (--org-muted #6db0ba): clearly
the org's own series (distinct from the grey England line) while still reading as
de-emphasised (thinner, dashed, not as bold as the solid reliable line); legend
swatch + note updated to match. Renders: v4_a_national, v4_b_provider (via
buttons), v4_c_search (org dropdown filtering "manchester"), v4_d_thin (muted-teal
low-reliability next to England), v4_e_prize (no selector, follows CMB31),
v4_f_breakdown_search. JS node --check clean. NOT DEPLOYED — paused for review.

## 2026-06-10 — Per-org breakdown FILTERING built (v3); PAUSED before deploy (Code, from per-org-filtering-spec.md)
Pipeline + front end. PIPELINE: build_site_data._breakdown_payload emits a NEW
org/<CODE>.breakdown.json per org (+ national.breakdown.json) carrying every
breakdown dim that exists (cancer/route/modality/combination) per standard, same
series shape as the all-slice. ~147KB raw / 20-37KB gz per org; 37.9MB raw total
— so GITIGNORED and rebuilt every run into the Pages artefact (same pattern as
downloads/); the lean all-slice org/<CODE>.json stays committed for fast first
paint. FRONT END: a custom in-DOM dropdown (not native <select>, so options are
reviewable + groupable) near the chart, default "All cancers". Fetched LOAD-ON-
DEMAND only when the filter is first opened (or a ?slice= deep link). Options
reshape per standard via dimsForStandard(): FDS28 = cancer only; CMB31/62 = cancer
+ route + modality + published pairwise combos (each combo a labelled option, no
two-dropdown Cartesian implication). Selecting a slice redraws only the big chart;
National comparison line MATCHES the slice (England lung vs org lung), aligned by
MONTH (robust to slices that skip months) and HIDDEN if no matching national slice
rather than falling back to all-cancers. Sub-threshold months (denom<10) SHOWN but
flagged: open grey markers AND the connecting LINE segments touching a sub-
threshold month are greyed + dashed (post-review fix — fragility must reach the
line, not just the dots, so a thin slice's 0%/100% bounces don't read as a real
collapse; same principle as the funnel carrying its own uncertainty). Drawn per-
segment, so an all-final above-threshold series is still a solid line. Empty slice
→ "No data published for this breakdown at this organisation." Switching standard/
org resets to All cancers and reshapes. Summary cards + size-of-the-prize STAY all-
cancers (per spec). Added a _breakdown_payload guard test (16 pass). Renders:
filt_a_lung.png (RRK CMB62 Lung + matched national + tooltip), filt_b_fds28_panel
.png (FDS28 cancer-only options), filt_c_thin.png (Acute leukaemia thin slice — now
greyed/dashed line + open markers + note). DEPLOYED (watched) after planning
approval; pause after.

## 2026-06-10 — CI: actions bumped to Node 24-capable majors + daily no-op commit removed; DEPLOYED (Code)
Two CI-resilience fixes ahead of the 16 Jun 2026 Node 20 removal (which would land
right next to the 11 Jun decommission). (1) Bumped checkout v4->v6, setup-python
v5->v6, upload-pages-artifact v3->v5, deploy-pages v4->v5; verified a dispatched
run green on all four with no Node 20 deprecation annotation. (2) The commit step
now skips when ONLY meta.json's built_at changed (git diff --cached with an exclude
pathspec), so no-op daily runs no longer create an "Auto update CWT data" commit
that every manual deploy had to rebase over — the freshly-built site/ (incl. fresh
meta.json) still deploys from the working tree. Verified: a no-op dispatched run
left origin/master HEAD unchanged. This is the only item this cycle that shipped.

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
