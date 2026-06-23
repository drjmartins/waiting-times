# Decisions log

Shared decisions across the two Claude sessions (Claude Code = pipeline/data/
infra/deploy; planning session = UX/audience/features/visual design). Newest
entries on top. Keep entries short (~3 lines): what, why, date, which session.

---

## 2026-06-23 — WCAG 2.1 AA accessibility pass DEPLOYING — full line nudge chosen, whole pass shipped together (Claude Code)

User chose **Option A (full nudge)** from the trade-off render. All three faint reference LINES wired to their
~3:1 values in the shared palette, one variable per line: low-reliability/provisional `--org-muted #6db0ba →
#4f9aa6` (2.45→3.23:1), England grey `--nat #9aa7ad → #838f95` (2.47→3.32:1), milestone `--milestone #b8a06a →
#a08a52` (2.54→3.36:1). Applied to cancer + rtt; compare.html got the `--nat` nudge (its centre England line +
sub-threshold rings). **1.4.11 is now a clean pass for the lines**, so the earlier "lean on shape+dash+legend
redundancy" conformance stance is MOOT / no longer load-bearing (the redundancy remains as belt-and-braces, not
as the argument). Hierarchy holds because the primary SOLID org line (`--org #0f7d8c`) is untouched — the nudged
lines are still lighter/dashed/dotted and read as secondary (render-verified headless on Airedale 62-day +
England 18-week).

Deployed as ONE pass with everything from the two prior 2026-06-23 entries (the four HIGH fixes + no-cost MEDIUMs
+ decoupled dark text labels). Commit + push + watched workflow_dispatch; STATUS.md updated. Live-verification
results (run number, criteria re-confirmed, reconciliation/ODS/provider-type guards) recorded once the watched
run lands.

## 2026-06-23 — WCAG 2.1 AA fixes BUILT + verified (no-visual-cost track); line trade-off rendered both ways — NOT DEPLOYED, awaiting line decision (Claude Code)

Built every no-visual-cost fix from the audit across all four pages; render-verified headless (2× Chrome) +
55 tests still pass. NOT deployed — paused for the user to pick the one real trade-off (faint line colours)
from the side-by-side render. Two tracks:

**BUILT NOW (shipped to working tree, both dashboards where shared):**
- **1.1.1 chart text alternatives.** Every chart `<svg>` now `role="img"` + `<title>`/`<desc>` + a generated
  `aria-label` summarising the on-screen slice. PLUS a visually-hidden `<table>` per big chart / funnel /
  percentile, built from the SAME clipped series the chart draws (can't diverge), with provisional /
  low-reliability flags as TEXT, respecting the current measure/group/TF/route/range/England-overlay. Verified:
  cancer big table 36 rows (matches the 3y/all window), RTT rate+count tables, compare funnel 157 / percentile
  139 rows. Sparklines got `role="img"` + latest-figure-and-trend `aria-label`.
  - GOTCHA fixed in verification: a `<table class="vh">` ignores `width:1px` (auto table layout) and rendered
    full-width → 787px horizontal overflow at 320px. Fix: wrap each table in a `<div class="vh">` (a block div
    respects width:1px and clips the table); the table no longer contributes to scrollWidth.
- **2.1.1 keyboard tooltips.** The transparent `.pt.hit` SVG points are now `tabindex=0` + per-point `aria-label`;
  the same tooltip the hover shows now also fires on `focus` (and hides on `blur`), with a visible focus ring
  (`.pt.hit:focus-visible`). Applies to both big charts + the funnel/percentile (compare positions the fixed
  tip from the point's bounding rect on focus). Verified: focusing a point shows the tip (cancer display:block;
  compare tip opacity→1).
- **4.1.2 name/role/value.** Segmented toggles (England/Providers/Commissioners, provider-type, time-range,
  long-waiter threshold) now carry `aria-pressed` reflecting the active state (set wherever `.active` is
  toggled); their containers got `role="group"` + a label. Summary cards got `role="button"` + `aria-pressed`.
  Listbox options got `aria-selected`. Fixed the illegal listbox: `role="listbox"` moved OFF the panel (which
  contained the search input) ONTO the options-only container, with `aria-controls`/`aria-label` wiring and the
  search inputs labelled. Expand modal: `role="dialog"` + `aria-modal` + accessible name, focus moved to the
  close button on open, focus trap on Tab, background `.wrap` set `inert`+`aria-hidden`, focus returned to the
  Expand trigger on close. Verified: dialog role/aria-modal present, wrap inert while open, focus returns to
  `#expandbtn` on close, option `aria-selected=true` on the active org.
- **4.1.3 status messages.** Added a polite `#live` region per page; chart re-renders + empty/"no data" states +
  the compare region-fallback note announce a concise summary. (`#fallback` also got `role="status"`.)
- **1.4.10 reflow @320px.** Relaxed the fixed min-widths (`min(360px,100%)`/`min(380px,100%)` + `max-width`),
  capped compare's native `<select>` with `max-width:calc(100vw - 48px)` + `.controls > div{max-width:100%}`
  (native selects size to their widest option), and let `.fgrp`/`.rangewrap` wrap so the long-waiter label+buttons
  don't overflow. Verified 0px horizontal overflow at 320px on all three (RTT longwait included).
- **1.4.1 link underline.** `.dashnav a` (landing/cancer/rtt) and compare's `nav a` now underlined (footer/source
  links already underlined by default — left as-is). compare `<title>` de-duplicated (2.4.2).
- **1.4.3 TEXT decoupling (no line change).** New `--target-text:#9a6600` (4.9:1) for the amber "below target"
  card label + the SVG "target NN.N%" label; `--milestone-text:#75632f` (5.9:1) for RTT milestone labels; the
  cancer low-reliability latest FIGURE (`b.muted`) switched from muted teal to `--ink` (keeps its n<10 caveat +
  muted sparkline). The amber/tan/teal LINE colours are untouched here.

**RENDERED BOTH WAYS (the one decision left to the user):** an Artifact compares the faint reference LINES at
(A) as-shipped vs (B) a gentle nudge to ~3:1 — the SAME real chart captured twice, only line colours differ.
Nudge palette: low-rel/provisional `#6db0ba→#4f9aa6` (2.45→3.23:1), England grey `#9aa7ad→#838f95`
(2.47→3.32:1), milestone `#b8a06a→#a08a52` (2.54→3.36:1). Artifact:
https://claude.ai/code/artifact/521e8392-4453-4951-a905-ce92cac703d0 — side-by-side + flip-in-place per chart,
plus Option A (clean 1.4.11 pass, slight hierarchy compression) vs Option B (leave faint, document the
shape+dash+legend redundancy as the conformance basis) and a middle path (nudge milestones only). AWAITING the
user's pick; the chosen line colours are a one-variable-per-line change in the shared palette.

## 2026-06-23 — WCAG 2.1 AA accessibility audit — REPORT ONLY, no fixes yet (Claude Code)

Audited all four live pages — landing (`site/index.html`), `/cancer/`, `/rtt/`, and `compare.html` (soft-hidden
but live) — against WCAG 2.1 AA. Audience is professional (NHS managers/analysts/clinicians), so NO plain-language
work; pure accessibility. Contrast ratios MEASURED (sRGB, WCAG formula). Fixes proposed but NOT built — user to
decide the design trade-offs (faint-state criteria) first. Verdict: **4 high-severity gaps, several medium.**

### Verdict by criterion
- **1.1.1 Non-text content — FAIL (HIGH, all pages).** Biggest gap, as predicted. Every chart is bare inline
  `<svg>` with NO `role="img"`, NO `<title>`/`<desc>`/`aria-label`, and NO data-table alternative: the two big
  time-series charts, the funnel + percentile plots (compare.html), and the card sparklines. A screen-reader user
  gets nothing (or a jumble of loose axis `<text>`). Sparklines are partly mitigated (the latest figure is real
  text on the card); the big charts and funnel are a total loss. Fix: add `role="img"` + a generated `aria-label`
  summarising the series (latest value, target, direction), AND a visually-hidden `<table>` of the on-screen
  months/values per chart (regenerated in renderBig/renderRate/renderCount/funnelSVG). No visual-design cost.
- **1.4.3 Contrast (minimum) — PARTIAL FAIL (MEDIUM).** Body text and most UI pass comfortably. The deliberately
  faint states are where it breaks. MEASURED on white/paper:
  - ink `#11202b` 16.6:1 ✓; ink-soft `#4a5a64` (labels, eyebrows, monospace bylines, axes, footer) 7.0–7.2:1 ✓
    — the muted bylines/eyebrows are FINE, contrary to the worry.
  - org teal `#0f7d8c` links/headings 4.7–4.9:1 ✓ (small-text pass, just clears 4.5). BUT teal text on the
    active-option tint `rgba(15,125,140,.10)` ≈ 4.2:1 — minor FAIL.
  - **Amber "▼ below NN% target" card label (`.vs.under` `#c8881d`, ~11px) = 3.00:1 — FAIL** (needs 4.5). Both
    dashboards. Paired with a ▼ glyph so not colour-alone, but contrast fails.
  - **Amber "target NN.N%" SVG margin label (`#c8881d`, 10px) = 3.00:1 — FAIL.** Big charts (both) + funnel.
  - **RTT recovery-milestone labels (`#b8a06a`, 9px) = 2.54:1 — FAIL.**
  - **Cancer low-reliability latest figure (`b.muted` `#6db0ba`, 27px bold = LARGE text, 3:1 threshold) =
    2.45:1 — FAIL even at the large-text bar.**
  - Passing text worth recording: good green `#2f7d4f` 5.0:1 ✓, card "n=…, low reliability" `#8a6d1f` 4.9:1 ✓,
    amber/red note boxes 6.6–8.3:1 ✓, tooltip text on dark ink 10–16:1 ✓, white-on-teal active button 4.85:1 ✓.
- **1.4.11 Non-text contrast (meaningful graphics, 3:1) — FAIL (MEDIUM).** The faint CHART LINES/markers fall
  below 3:1 vs white: low-reliability/provisional muted teal `#6db0ba` 2.45:1; grey England line `#9aa7ad`
  2.47:1; milestone line `#b8a06a` 2.54:1. Amber target line 3.0:1 (borderline ✓). Gridlines `#eef3f4` 1.12:1
  and control borders `#d7e0e3` 1.34:1 are decorative/non-essential (gridlines exempt; control identity is also
  carried by text labels). NOTE the get-out: these series ALSO encode state by shape+dash + legend, so colour is
  not the sole carrier — a defensible argument that 1.4.11 (which targets graphics "required to understand")
  is softened. Document the stance rather than necessarily darkening.
- **1.4.1 Use of colour — MOSTLY PASS, one FAIL (MEDIUM).** Charts pair colour with shape+dash (provisional =
  open circle + dashed; low-reliability = open square + dotted; final = filled solid; England = solid grey vs
  teal) ✓. Cards pair colour with ✓/▼ glyphs ✓. Funnel uses fill (direction) + size (severity), not hue ✓. The
  org-lifecycle "related org" links are underlined ✓. **FAIL: the footer source links (and dashnav/card links)
  are teal with `text-decoration:none`** — distinguished from surrounding text by colour ONLY; inline footer
  links vs surrounding ink-soft = 1.47:1 (well under the 3:1 that would let colour-alone pass), and underline
  appears only on `:hover` (not keyboard/touch/persistent). Fix: persistent underline on in-prose links.
- **2.1.1 Keyboard — MOSTLY PASS, one FAIL (HIGH).** All real controls are keyboard-operable: native
  select/checkbox/inputs (compare.html), the custom dropdown TRIGGERS are `<button>`s, panel options are
  `<button role=option>` (reachable by Tab, Enter activates; search box focuses on open, Enter = first match,
  Esc closes), segmented buttons are `<button>`, cards are `div tabindex=0` with Enter/Space handlers, expand
  toggles + Esc, download menu. **FAIL: chart tooltips are `mouseenter`/`mouseover`-only** — the per-point
  exact data (month, %, numerator/denominator, final vs provisional) is revealed on hover with no keyboard
  path; SVG points have no tabindex/role and the data exists nowhere else. Affects all four pages.
- **2.4.7 Focus visible — PASS (with caveat, LOW).** No `outline:none` and no custom focus CSS anywhere, so
  the UA default focus ring is intact on every focusable element (verified: zero `:focus`/`outline` rules).
  Caveat: relies entirely on browser defaults; the default ring can be low-contrast on the teal active button
  and inside dropdown panels. Recommend an explicit `:focus-visible` ring (2px, ≥3:1) — robustness, not a
  current failure.
- **2.4.3 Focus order / modal — FAIL (MEDIUM).** The expand modal MOVES the live panel into the overlay, so
  focus happens to ride along on the moved node (rough return-on-close), and Esc/backdrop close work. BUT: focus
  is not explicitly sent to the dialog, there is NO focus trap, and the background is neither `inert` nor
  `aria-hidden` — keyboard/SR users can Tab out into the page behind the modal. Fix: trap focus, focus the close
  button on open, restore on close, hide the background.
- **4.1.2 Name/role/value — FAIL (HIGH).** Custom controls don't expose state to a screen reader:
  - Dropdowns: `aria-expanded` IS toggled correctly ✓, but the panel is `role="listbox"` containing a search
    `<input>` (invalid listbox child) and the options carry NO `aria-selected` — the chosen org/group/route/TF
    is a visual `.active` class only. Arrow-key listbox navigation isn't implemented either.
  - Segmented toggles (England/Providers/Commissioners, provider-type, time-range, long-waiter threshold): no
    `role`/`aria-pressed`/`aria-selected`; the active state is colour-only and invisible to SR.
  - Summary cards: `<div tabindex=0>` with no `role` and no selected-state exposure (they're a tab/switcher).
  - Expand modal: container has no `role="dialog"`, `aria-modal`, or accessible name; download trigger lacks
    `role="menu"`.
  - Good, keep: `aria-current="page"` on nav ✓; native checkbox+`<label>` "Show England" ✓; compare.html native
    `<select>` + `<label for>` ✓ (its controls are MORE accessible than the dashboards' custom ones).
  Fixes are non-visual (add `aria-pressed`/`aria-selected`, dialog semantics) — no design cost.
- **4.1.3 Status messages — FAIL (MEDIUM).** Chart re-renders on every control change, the "No data published"
  / empty-slice states, the compare.html region-fallback note, and live-filtered option counts all appear with
  no `aria-live` region — SR users get no feedback that anything changed (compounding 1.1.1). Fix: a polite
  live region announcing the active slice + a one-line summary.
- **1.4.10 Reflow (320px) — FAIL (MEDIUM).** Charts scale cleanly (`viewBox` + `width:100%`). BUT fixed
  min-widths force horizontal scroll at 320px (content box ≈ 272px after 24px padding): cancer/rtt org button
  `.orgbtnwrap .filterbtn{min-width:380px}` and `select,input[type=search]{min-width:360px}`. Fix: cap with
  `min-width:min(360px,100%)` / `max-width:100%`. compare.html (`select{min-width:240px}`) is OK.
- **1.4.4 Resize text (200%) — PASS (borderline).** Sizes are px but browser zoom scales them, the viewport
  meta does NOT disable zoom, and controls wrap; usable at 200%. The same fixed min-widths could clip at very
  high zoom on small screens — fold into the 1.4.10 fix.
- **Minor:** compare.html `<title>` duplicates the cancer-index title (2.4.2); heading order has card `<h3>`s
  before the chart `<h2>` (1.3.1/2.4.6); no `<main>` landmark (1.3.1 best-practice).

### Shared-component note
Cancer and RTT share the palette and nearly all front-end mechanics (picker, segmented controls, cards,
dropdowns, big-chart renderer, expand/export, tooltips). So almost every fix lands in BOTH: SVG text
alternative, keyboard tooltips, `aria-selected`/`aria-pressed`, dialog semantics, live region, and the
min-width reflow cap all apply to both dashboards. The amber/muted contrast values are identical across both
(same vars). compare.html is the odd one out (native selects, simpler) — it needs the SVG/keyboard fixes but
its form controls are already fine.

### Design trade-offs to settle BEFORE any build (these touch the tuned chart language)
1. **Faint lines vs 1.4.11 (3:1).** Darkening `--org-muted`/`--nat`/`--milestone` to clear 3:1 makes the
   de-emphasised states less faint — directly against the intent. Defensible alternative: KEEP the lines faint
   and lean on the existing shape+dash+legend redundancy (argue colour isn't the sole carrier), documenting the
   stance. Or nudge only enough to reach ~3:1 (a small darken still reads as "muted" beside the strong teal).
2. **Amber/muted TEXT labels have a HARD bar (4.5:1 small / 3:1 large) with no shape get-out.** Recommended:
   DECOUPLE label colour from line colour — keep the target/milestone LINES their tuned amber/tan but render
   their TEXT labels in a darker tone (ink-soft or a darkened amber) so the line stays faint while the text
   passes. Same for the cancer low-reliability latest figure: keep the figure in dark ink (it already carries a
   "n=…, low reliability" text caveat + a muted sparkline), rather than colouring the 27px number itself muted.
3. **In-prose link underline (1.4.1).** Persistent underline on footer/source + dashnav links is a small visual
   change to a deliberately clean look — user to confirm scope (footer-only vs all).
Items not touching the visual language (do regardless): SVG text alternatives, keyboard tooltip access,
`aria-selected`/`aria-pressed`/dialog semantics, live region, reflow min-width cap, explicit focus-visible.

---

## 2026-06-23 — DEPLOYED + LIVE-VERIFIED: consistency-cluster round — RTT region, soft-hidden comparator, compare-this-trust link, nav A (Code)

DEPLOYED run 28019834569 (build+deploy GREEN; CI commit 9dbac27). Live-verified on the deployed site (curl +
headless): RTT region beside provider (RCF→NE&Y, independents/ICBs/National none; 162/594 real), comparator
link gone from cancer UI + compare.html still 200s, compare-this-trust in markup but hidden, nav consistent
across all 3 with current marked, compare.html ?org=RCF → region scope + highlight. CI: 55 tests, RTT recon
OK + TF-sum max|Δ|=0, ODS LIVE fetch both pipelines (427 orgs/556 trust codes), guards intact. ODS ordering
note: in CI cancer builds before RTT, so RTT reads a fresh cancer index for regions. Tests 53→55. Detail:

**1. RTT region in provider picker (BUILT).** Premise correction: the RTT org records carried a `region`
FIELD but it was a hardcoded placeholder ("England" for all 594 providers — the RTT "Full CSV" source has
no provider region, only a Commissioner Parent/ICB). So this needed a real source, not just UI wiring.
Decision: reuse the region the CANCER dashboard already derived (its Parent_Org-based region, the
authoritative NHS source), keyed by org code — so an RTT trust's region is identical to the same trust's
cancer region by construction ("same field"). New shared helper `pipeline_common/regions.py:load_region_map`
reads the committed `site/cancer/data/index.json` and returns {code: region} for non-England codes; RTT
`build.py` applies it to PROVIDERS only (ICBs stay "England", matching cancer). Fail-open: missing cancer
index → {} → everything defaults to "England" (regions just don't show that build). Front-end RTT `render()`
now sets the `#orgname` byline with cancer's exact logic (the element/CSS/`.orgrow` layout already matched).
Rebuilt from local zips: both gates green (SPN pct18 0.5973 / waitlist 7,389,065; TF-sum max|Δ|=0); 162/594
providers got a real region, **0 mismatches** vs cancer across 163 shared codes; RTT-only independents (e.g.
NPR01) + ICBs + National show nothing, exactly like region-less cancer providers. Verified: RCF → "North
East and Yorkshire" beside the dropdown.

**2. Soft-hide the CWT comparator (BUILT).** Added one CSS rule `.compare-soft-hidden{display:none!important}`
in cancer/index.html and wrapped the header "Compare Providers (Beta)" link + its trailing `|` separator in
that class. compare.html stays live (direct URL still 200s) — just not reachable by clicking. **Reversal =
delete that one CSS rule** (un-hides BOTH the header link and the per-org link from #3 together). Verified:
header now reads "RTT Waiting Times Dashboard → | All dashboards", no dangling separator, 0 visible
compare links.

**3. Compare-this-trust link (BUILT, soft-hidden).** Per-org "Compare this trust →" link added to the
cancer `.orgrow`, using the SAME `.compare-soft-hidden` class so it un-hides with #2 (no rework). JS
`syncCompareLink()` keeps it PROVIDER-ONLY (hidden for National/ICB via the `hidden` attribute, which takes
over once the soft-hide class is removed) and sets href = `compare.html?org=<code>&std=<std>`. compare.html
gained a minimal `?org=` consumer: captures it in init, scopes the funnel to that trust's NHS region once
(unless an explicit `?scope=` is also given), and draws a gold emphasis ring + bold name label on the
trust's point in BOTH the funnel and percentile views. Kept additive/isolated so it doesn't disturb the
in-flight comparator iteration. Verified via direct URL: `?org=RCF` → scope auto-set to "North East and
Yorkshire", Airedale ringed + labelled.

**4. NAVIGATION — Option A BUILT (user chose A, incl. landing).** A single consistent monospace `.dashnav`
strip on ALL THREE pages: `Cancer · RTT · All dashboards`, same order/separators (`·`) everywhere, current
page rendered as bold non-link text with `aria-current="page"` (landing marks "All dashboards"; cancer marks
"Cancer"; rtt marks "RTT"). Old per-page arrow grammar (cancer trailing `→`, rtt leading `←`) and `|`
separators dropped. The soft-hidden "Compare Providers (Beta)" link rides at the end of the cancer strip
inside `.compare-soft-hidden`, so deleting that one CSS rule restores BOTH it and the per-org compare link.
~7 lines CSS + a 4-line `<nav>` per page; static files, no templating, so the strip is duplicated across 3
files (acceptable at 2 dashboards). UPGRADE PATH: when a 3rd dashboard lands, replace the strip with Option
B — a shared persistent top bar + segmented switcher (matching the Providers/Commissioners toggle) — and at
that point consider injecting it via the render step to avoid 3-file drift. Verified all three: current
marked, correct cross-links, Compare link in markup but not visible on cancer.

(original report) Current top nav: landing has NO switcher (only
two cards + a footer); cancer shows `[Compare(hidden)] | RTT Waiting Times Dashboard → | All dashboards`
(trailing → grammar, no current-page marker); rtt shows `← Cancer Waiting Times Dashboard | All dashboards`
(leading ← grammar, no marker). Inconsistencies: mismatched arrow grammar, no "you are here" on either, no
unified switcher, landing absent from any header band. Option A (light touch): one consistent monospace
header strip on both dashboards (and optionally landing) listing the same ordered peers with the current
page marked (non-link, bold) and unified separators — ~15 lines/page, near-zero risk. Option B (fuller):
a shared persistent top bar on all 3 pages with a segmented [Cancer | RTT] switcher (active segment filled,
matching the existing Providers/Commissioners toggle grammar) + brand label — more native-feeling, scales to
3+ dashboards, but must be duplicated/kept-in-sync across 3 static files (no templating). **Recommendation:
A now** (closes the actual inconsistencies cheaply, reversible, clean upgrade path), move to **B when a third
dashboard lands**. User to choose before build.

## 2026-06-22 — DEPLOYED + LIVE-VERIFIED: footer-accuracy reword, BOTH dashboards (Code)

Hiding is org-type-AGNOSTIC (verified live: the inactivity rule keys on recent activity, not type —
cancer hides 34 NHS trusts + 17 independent; RTT 22 + 42), so the RTT footer's "independent-sector providers
… are hidden" was misleading. Reworded both (user-approved final copy):
 - RTT: "Providers with very little recent activity (no month reaching 100 on the waiting list in the past
   year) are hidden. Non-English-commissioned activity is also excluded."
 - Cancer: "Organisations with very little recent activity (for providers, no standard reaching at least 10
   patients in a single month over the last year; for commissioners, very low recent total volume) are
   hidden."
Provider-type-filter mention deliberately dropped (toggle self-evident in the UI). Deployed run 27966254999
(GREEN). Live-verified: both footers render with the new copy, clean punctuation, dynamic dates intact
(RTT "Data to April 2026. Last updated 22 June 2026"; cancer "Data to March 2026 …"). No test asserted on
the old text. 53 tests pass.

## 2026-06-22 — DEPLOYED + LIVE-VERIFIED: scope the "Formed" note to genuine recent formations, BOTH dashboards (Code)
(Deployed run 27964831412, build+deploy GREEN; CI commit pending. Live: RTT RTH/R1L/QRL → no note, Z9B2Z →
Formed note, QNQ → Former note unchanged; cancer RTH → no note, QNQ → Former unchanged. CI: ODS live fetch
(556 trust codes), recon OK, TF-sum maxΔ=0, provider-type guards passed. Footer-accuracy reword handled
separately — report-first.)

Bug: the "Formed / new organisation … earlier months not available" note fired on ANY current org with
predecessor links, regardless of age — wrongly showing on long-established trusts (e.g. Oxford University
Hospitals RTH, formed 2011, full history since Apr-2022). Fix keys off the DATA, leaving the Closed/Former
note UNCHANGED (asymmetric — a closed org's history IS here and pointing to successors is always useful).

FINDING (contradicts the brief's assumption, surfaced from the data): the brief's rule — show when
(data series truncated past the Apr-2022 floor) AND (has predecessor links) — STILL over-fires. ~13 cancer
"providers" are long-established MENTAL-HEALTH / AMBULANCE trusts (Essex Partnership f.2017, Sussex
Partnership, London Ambulance, Kent & Medway, …) whose CANCER series merely starts late (little cancer
activity), yet they DO carry old-merger predecessor links — so truncation+predecessors alone would put a
misleading "Formed" note on them (same bug class). The brief expected late-reporters to lack predecessor
links; the data shows they don't.

REFINED RULE (achieves the brief's intent; deviation flagged): show the Formed note only when BOTH —
 (a) series_truncated: data starts > floor + ~2-month margin (keyed off DATA, no ODS date); AND
 (b) formed_recently: the org has a predecessor that ITSELF closed within the data window (closed >= floor)
     — a genuine recent HANDOFF, using the reliable succession CLOSE-dates (not the sparsely-populated /
     unreliable ODS formation date the brief warned against; opened is None for most of the false positives).
 Both are required: truncation alone over-fires on late-reporting established trusts; the handoff alone
 would fire on a boundary GAINER like QRL (gained Frimley territory but kept full history → not truncated).

VERIFIED (rebuild + re-render both): formed-note orgs went 74-candidates → cancer 0 (the 6 new 2026 ICBs
aren't in cancer data yet — publication lag; all 13 MH/ambulance false positives gone), RTT 6 (exactly the
new 2026 ICBs D7T5G/S0E4D/S1Y5D/S9B9J/T6Y0W/Z9B2Z). RTH Oxford → NO note (both); R1L Essex Partnership → no
note; QRL → no note (boundary gainer, full history); QNQ/Frimley → Former note UNCHANGED (both); Z9B2Z →
Formed note shows. G6V2S (real 2024 MH-trust merger) correctly absent — not in RTT data (no elective
pathways), so not a false negative. 53 tests pass (added series_truncated / formed_recently / QRL-gainer +
former-asymmetry cases). Shared logic in pipeline_common/ods.py; both builds pass formed_ok. Open: deploy
on say-so.

## 2026-06-22 — DEPLOYED: RTT "Independent Sector empty" diagnosis + empty-set guards + CACHE-BUST (Code)

Reported: live RTT shows ALL providers under NHS Trusts, Independent empty (cancer fine). INVESTIGATED —
the matching is NOT broken and the deployed data is CORRECT:
 - Live RTT index.json tags 423 providers `independent`; all 171 non-independent providers are GENUINELY in
   the ODS nhs_trust_codes set (matched, ZERO fall-through). Cancer 173 matched / 28 independent. Code forms
   match fine (RTT mixes 3-char trusts like RCF + 5-char IS like NPR01; the ODS set has both).
 - Fresh headless load of the LIVE site renders 381 independents in the RTT dropdown; live index.html
   contains the filter logic. So server-side artefacts are correct.
 - CAUSE = client-side STALE-CACHE SKEW: a browser-cached PRE-ptype index.json (from the previous deploy)
   paired with the new index.html → every provider untagged → fail-open → "all NHS Trusts". A hard refresh
   resolves it. (No cron ran between deploy and the report; nothing regressed server-side.)
 - The symptom ("all NHS Trusts") requires UNTAGGED providers, which at BUILD time happens only if
   nhs_trust_codes is empty — note a total code-form MISMATCH would instead tag everything INDEPENDENT, the
   opposite. So the real latent build risk is an EMPTY trust set (transient ODS failure + no cache), which
   would silently ship the all-default and pass every existing gate. That is the gap fail-open left.

GUARD ADDED (the paired check fail-open was missing), two layers, both fail-loud BEFORE publish:
 - ods.assert_independents_tagged(index, label, trust_codes): when a trust set IS present, a dashboard with
   providers MUST tag >0 independents — else raise (catches a populated-set match failure). Called in both
   builds after the index is assembled. Skipped when trust_codes is empty (synthetic/dev/tests, where
   typing isn't attempted) so it can't false-fire.
 - both real run.py entrypoints: refuse to build if refresh_or_cache returns an empty nhs_trust_codes (live
   fetch AND committed cache both empty) — catches the actual empty-set production case the build guard
   skips. Together: neither an empty trust set NOR a zero-match can silently ship the all-NHS-Trust default.
 - +1 test (guard raises on populated-set/zero-independent; OK with an independent present; skips on empty
   set). 52 pass. NOT changing the tagging logic (it's correct on both dashboards).

CACHE-BUST ADDED (the actual recurrence-fix, BOTH dashboards): every data file except meta.json is fetched
via durl(path) which appends `?v=<token>` where token = meta.built_at digits (DYNAMIC — changes every build
that changes the data; no hand-bumped string). meta.json is fetched `{cache:"no-store"}` so the token always
reflects the latest deployed build (tiny file). Because `?v=` is part of the HTTP cache key, a browser/CDN-
cached index.json (bare, or an older ?v) can NEVER satisfy the new build's index.json?v=<new token> request
→ a new index.html structurally cannot pair with a stale index.json. Verified locally: requests carry
?v=20260622141518988596 on national/index/org/breakdown; meta.json stays bare/no-store; page renders (381
independents). compare.html left as-is (separate page, no ptype dependency, lower risk).

DEPLOYED + LIVE-VERIFIED (run 27962238975, build+deploy GREEN; CI commit a11c663). CI: ODS live fetch ran
for both pipelines (556 trust codes), both RTT gates passed, NO "refusing to publish" (both guards passed on
real data). Live: RTT Independent Sector POPULATED (423 tagged / 381 visible), cancer unchanged (28 tagged /
11 visible); data requests carry ?v=<built_at token> (e.g. index.json?v=20260622151047991743) while
meta.json stays bare/no-store; token differs per build → a cached stale index.json (different cache key)
can't pair with the new HTML. Both guards demonstrated firing on bad inputs; synthetic/test path skips.
recon + TF-sum gates + ODS fail-soft intact.

## 2026-06-22 — DEPLOYED + LIVE-VERIFIED: provider-TYPE picker filter, BOTH dashboards (Code)

Confirm-data-first then build + deploy (run 27958596878, build+deploy GREEN; CI commit f7adeee). A
provider-type sub-filter scopes the org dropdown on the Providers view (England/Commissioners unaffected):
segmented [NHS Trusts | Independent Sector], **default NHS Trusts** (independent-sector opt-in). 51 tests.
LIVE-VERIFIED on both: ptype tags present (cancer 173/28, RTT 171/423, no ICB tagged); default Providers =
NHS Trusts (Airedale RCF); switch → Independent re-scopes (RTT About Health HQ NPR01 / cancer Assura NYT);
deep-link ?org=NPR01 / ?org=NYT → filter AUTO-SWITCHES to Independent and shows the org. CI log: ODS live
fetch ran for both pipelines (556 trust codes, as_of 2026-05-07 — not the fallback); both RTT gates intact
(recon OK, TF-sum max|Δ|=0); ODS fail-soft path unchanged.

DATA CONFIRM (per dashboard, by ODS PRIMARY role; reversed the going-in assumption):
 - Cancer 201 providers → 173 NHS Trust / 28 Independent Sector / **0 residue** — a CLEAN two-way split.
   The name-based "Other" (~28) that earlier looked murky is, by ODS role, ALL independent-sector
   (RO172/RO176). The murk was the NAME heuristic, not the data.
 - RTT 594 → 171 NHS Trust / 422 IS / **1 residue**: 8KL73 ENDOCARE DIAGNOSTICS, role RO157
   "NON-NHS ORGANISATION" (and already hidden). 
 - DECISION (user-confirmed): define the split as NHS trust (RO197/RO107) vs non-NHS-trust (everything
   else), so the lone RO157 org + any future odd role fold into Independent Sector → BOTH dashboards are a
   clean two-way split, **no "Other" bucket**. Result: cancer 173/28, RTT 171/423.

BUILD:
 - pipeline_common/ods.py: added RO107 (Care Trust) to ROLES; emits `nhs_trust_codes` (primary role in
   TRUST_ROLES=RO197/RO107, all statuses, 556 codes) into the shared cache; `tag_provider_type(entry,
   trust_codes)` tags only independents (`ptype:"independent"`; absent => NHS trust = default view; empty
   trust set => untagged = fail-open). refresh_or_cache() now returns the FULL data dict {orgs,
   nhs_trust_codes,...}; both run.py pass orgs + trust_codes into the builds. Org-type split is pure ODS
   role data — no name heuristic.
 - Both builds tag provider index entries with ptype (ICBs never tagged). Cancer 173/28, RTT 171/423; no
   ICB tagged.
 - Front end (both, identical): new "Provider type" segmented control between the type buttons and the
   dropdown, shown for Providers only, default NHS Trusts. orgListFor filters providers by PTYPE; the
   redundant name-based NHS-Trust/Independent picker sub-grouping is REPLACED by the filter (picker now
   shows Current + Former only for providers; ICBs keep ICB/Other/Former). DEEP-LINK SAFETY: setType
   follows a requested org's ptype (filter switches to show the linked org, never hides it); setPtype
   re-scopes + selects the first org so the chart never blanks.
 - independent-sector providers are now opt-in on the default view (the ~32 young IS clinics no longer
   clutter the default RTT list — intended).
 - +1 test (tag_provider_type: trust untagged / non-trust independent / empty-set fail-open). 51 pass.

VERIFIED (re-render both): default Providers → "NHS Trusts" active, first trust (Airedale RCF); switch to
Independent Sector → list re-scopes (RTT: ACES… ; cancer: Assura/Ellenor/HCA…); deep-link ?org=NPR01 (RTT)
/ ?org=NYT (cancer) → filter AUTO-SWITCHES to Independent and shows the linked org. Open: deploy on say-so.

## 2026-06-22 — DEPLOYED + LIVE-VERIFIED: ODS org-status feature + Part A RTT copy (Code)

Shipped together in one watched workflow_dispatch (run 27948177203, build 10m32s + deploy 16s, BOTH GREEN;
CI committed rebuilt data as aa3c52b). User accepted the ~32 newly-surfaced IS clinics as-is and left
YOUNG_WINDOW_MONTHS=12 simple. Pushed to master, rebased over two intervening cron data commits.

EXPLICIT live verification (headless render + curl + CI log — not assumed):
 - Both dashboards + data 200. meta.built_at = today on both.
 - ODS fetch RAN IN CI for BOTH pipeline steps ("ODS: classified 416 succession-affected orgs (344 former),
   as_of 2026-05-07") — the LIVE path, not the cache-fallback message.
 - Both RTT fail-loud gates intact + passing: recon OK @2025-04 (pct18 0.5973, waitlist 7,389,065), TF-sum
   24,776 org-months reconcile exactly (max|Δ|=0). Cancer rebuilt (no new data; still Mar-2026).
 - QNQ/Frimley: in "Former organisations" group, SELECTABLE, 48 months history to Mar-2026, note "Closed
   April 2026 … see related: NHS Thames Valley / Surrey & Sussex / Hampshire & IoW (= S0E4D, S9B9J, QRL)".
 - Z9B2Z (West & North London): current, NOT hidden, SHOWN from its single Apr-2026 month, "Formed April
   2026 … drawing on the areas of NHS North Central London + NHS North West London" note. All 6 new RTT
   codes present + shown.
 - "Former organisations" picker group renders on BOTH dashboards (ICB type, search "essex").
 - Part A copy live on RTT: subtitle "… & waiting lists", reworded Feb-2024 banner, trimmed footer with
   DYNAMIC dates ("Data to April 2026. Last updated 22 June 2026").
 - UN-HIDE-ONLY confirmed live: RTT hidden 96→64, cancer 66→59; live_hidden ⊆ before_hidden on both;
   ZERO previously-visible orgs wrongly dropped.
 - FAIL-SOFT re-confirmed: simulated ODS outage (unresolvable host) → fell back to the committed 416-org
   ods_classification.json, never raised, QNQ still classified, build path runs.
 - Classification cache = committed BUILD INPUT at repo root (CI git-adds it); deliberately NOT in the Pages
   artefact (site/) — the classification reaches users baked into index.json, the cache only fail-soft-seeds
   the next build. (Confirmed /ods_classification.json is 404 on Pages, present on origin/master.)
 - Cancer's 6 new ICB codes still absent (data ends Mar-2026 = publication lag); they appear automatically
   when April CWT publishes. Both dashboards key ICBs on the same ODS codes.

## 2026-06-22 — BUILT (paused pre-deploy): self-updating ODS org-status feature, BOTH dashboards (Code) — SUPERSEDES the pooling proposal below

User killed pooling entirely (too risky/messy — incl. the clean Z9B2Z case). New direction: a fully
hands-off, self-updating org-lifecycle feature, no pooling / no apportionment / no human approval step.
New orgs show their own real (initially short) series; no fabricated history. Design was confirmed before
build; built + re-rendered + tested; **NOT deployed** (deploys with Part A on user's say-so). 50 tests pass.

THREE lifecycle states (kept distinct): CURRENT (live per ODS → main list) · FORMER (closed/superseded per
ODS → "Former organisations" picker group, STILL SELECTABLE — history stays viewable) · HIDDEN (a FORMER
org that ALSO trips the existing inactivity rule → out of the picker, data retained + ?org= reachable).
Supersession and hiding are two separate events in time; a newly-superseded org is NOT hidden immediately.

LOAD-BEARING CORRECTION (user credited): classify FORMER from the **succession link whose legal start has
passed**, NOT `Status`. Verified live 2026-06-22 that ODS keeps closed orgs `Status:Active` through a
~6-month migration overlap (all 12 ICBs + Frimley still "Active"), so Status alone misses every current
merger. `Status==Inactive` kept only as an additional catch-all (post-overlap).

WHAT WAS BUILT:
 - `pipeline_common/ods.py` (NEW shared module, both pipelines import it). Reads the free no-auth ODS ORD
   REST API (directory.spineservices.nhs.uk/ORD/2-0-0). Fetches role summaries (RO261 ICB + RO197 NHS
   Trust/FT — verified both trusts AND FTs are RO197), then full records only for recently-changed /
   inactive orgs (→ a few dozen GETs, not 600+). Emits {code: {name,status,closed,opened,successors,
   predecessors}} for succession-affected orgs only; absent code => CURRENT (fail-open). ORG-TYPE-AGNOSTIC
   by the role list — future trust/provider mergers picked up by widening ROLES, no rebuild.
 - FAIL-SOFT (verified): `refresh_or_cache()` tries live, on ANY error returns the last-known committed
   cache and NEVER raises (data update can't crash on the new dependency); missing cache => {} (fail-open,
   never drops orgs). ONE SHARED committed cache `ods_classification.json` (user's call — same truth for
   both, can't drift; added to CI `git add`). `as_of` stamped from the STORED orgs' max LastChangeDate
   (ODS-derived, not per-run) so it commits only on real ODS change (respects the no-op-commit guard).
 - DATA MODEL: additive index.json fields, mirror the existing `hidden` flag — `former:true`, `closed`,
   `opened`, `related:[{code,name}]`, `reltype:"superseded"|"formed"`. Names stored (not just codes) so a
   note resolves even when the related org isn't in THIS dashboard's data yet. No change to series files.
 - HIDING REVISED (two rules, different jobs — user confirmed both stay): YOUNG (current per ODS + series
   first-appears within config.YOUNG_WINDOW_MONTHS=12) is checked FIRST and never hidden → new orgs show
   from month one (the existing "no year-ago data" note + n<10 flag carry the thin view). The inactivity
   rule still hides former-dormant orgs AND the pre-existing current-but-defunct codes. Net effect un-hides
   only (RTT hidden 96→64, cancer 66→59); never over-hides.
 - FRONT END (both, near-identical pickers): `orgGroupOf` buckets `former` orgs into a trailing
   "Former organisations" group (still selectable); a neutral `#orgnote` shows a GENERIC auto note built
   from the succession fields — former → "Closed <month>. … see related organisations: X, Y. Its figures
   up to closure remain viewable here."; new → "Formed <month>. … drawing on the areas of: …". Related
   orgs are clickable (goToOrg) when present in this dashboard, else plain text+code. No hand-written
   per-merger copy.

VERIFIED (re-rendered both): RTT former QNQ/Frimley → note lists its 3 successors (incl QRL), full history
through Mar-2026 selectable; RTT young Z9B2Z (West & North London) → single Apr-2026 month SHOWN (not
hidden), "Formed April 2026" note, "no year-ago data" cards; picker shows ICB + "Former organisations"
groups. Cancer (data ends Mar-2026, so no new codes yet — publication lag): 12 ICBs flagged former with
notes; successors not-yet-in-cancer render as plain text (S0E4D/S9B9J) while QRL (present) is a live link —
the graceful-degradation the stored-names design buys. Cancer gets the young new codes automatically when
April CWT publishes; RTT already has them. Both keyed on the same ODS codes (confirmed).

NOTED FOR USER (review): young-protection surfaced ~32 brand-new small independent-sector clinics in RTT
(ACES/Optegra/SpaMedica chains, 1–6 months) into the main list — a faithful consequence of "show young
from month one"; YOUNG_WINDOW_MONTHS (12) is the single knob to tighten if that's too lenient (it currently
== "lacks a full year of history" == shows the "no year-ago" note, a coherent definition). Open: deploy
this + Part A together on say-so.

## 2026-06-22 — Part A SHIPPED (RTT copy ×3) + Part B INVESTIGATION (ICB-merger handling, BOTH dashboards — report/propose only, no build) (Code)

### Part A — three RTT copy changes (BUILT, site/rtt/index.html, re-rendered + verified) ✅
Front-end-only, no pipeline/data change. (1) Feb-2024 banner → "⚠ Community services moved out of RTT
reporting in February 2024; figures before that month are not directly comparable." (dropped the bold
"series break" lead-in + the dashed-marker sentence — the marker still renders, ask if the explanation
should return). (2) Footer trimmed to data-source + OGL + independence line; the derivation/"official RTT
dashboard" sentence removed; non-English-commissioned note moved to the closing line: "Some
independent-sector providers with very little recent activity are hidden. Non-English-commissioned
activity is also excluded." Dates CONFIRMED DYNAMIC (`${latest}`=fullMonth(months[-1]), `${built}`=
isoDate(built_at) from meta.json, same mechanism as cancer footerHTML) — current meta renders "Data to
April 2026. Last updated 20 June 2026" (built_at=2026-06-20; next cron flips to 21 Jun automatically; the
"21 June" in the brief was illustrative). (3) Subtitle "… & the waiting list" → "… & waiting lists".
Headless render confirms all three strings; no test asserts on the old copy.

### Part B — ICB-merger handling: INVESTIGATION + PROPOSAL (no build; user decides before any build)
Source of truth: NHS ODS "ICB Mergers Phase 1 April 2026" change-summary xlsx PLUS — decisively — the
live ODS ORD REST API (directory.spineservices.nhs.uk/ORD/2-0-0/organisations/<code>, free, no auth,
JSON). Both dashboards key ICBs on the 3-char (old) / 5-char (new) ODS ICB code, level:"icb" — CONFIRMED.
RTT data already carries all 6 new codes (single month, Apr-2026) AND the 12 old; cancer carries the 12
old + QRL but NONE of the 6 new YET — purely a publication-lag artefact: cancer data ends 2026-03, new
codes are effective 2026-04, so they land the moment April-2026 CWT publishes. Symmetric, imminent, BOTH.

**1. EXACT old→new mapping — pulled live from ODS `Succs` (Successor links), matches the xlsx SICBL
groupings exactly:**
```
QHG Beds Luton & MK        → S1Y5D                      (whole)
QUE Cambs & P'boro         → S1Y5D                      (whole)
QM7 Herts & West Essex     → S1Y5D + D7T5G              (SPLIT — 2 successors)
QH8 Mid & South Essex      → D7T5G                      (whole)
QJG Suffolk & NE Essex     → D7T5G + T6Y0W              (SPLIT — 2 successors)
QMM Norfolk & Waveney      → T6Y0W                      (whole)
QMJ North Central London   → Z9B2Z                      (whole)
QRV North West London      → Z9B2Z                      (whole)
QU9 Bucks Oxon & Berks W   → S0E4D                      (whole)
QNQ Frimley                → S0E4D + S9B9J + QRL         (SPLIT — 3 successors; 3rd is the EXISTING QRL)
QXU Surrey Heartlands      → S9B9J                      (whole)
QNX Sussex                 → S9B9J                      (whole)
```
New-ICB predecessor view (reciprocal Predecessor links, also live): S1Y5D←{QHG,QUE,QM7}; D7T5G←{QJG,QM7,
QH8}; T6Y0W←{QMM,QJG}; Z9B2Z←{QMJ,QRV}; S0E4D←{QNQ,QU9}; S9B9J←{QNX,QNQ,QXU}. QRL is RETAINED (Active,
keeps code) and gains a Predecessor link from QNQ = the Frimley boundary transfer.

**2. CLEAN vs MESSY (decision rule: a new ICB is a clean whole-ICB union iff EVERY predecessor has exactly
ONE successor; split orgs are QM7, QJG, QNQ):**
 - **Z9B2Z West & North London = QMJ + QRV — the ONLY fully-clean union.** Both predecessors wholly
   absorbed → pool = exact sum, reconciles, verifiable. AUTO-POOL candidate.
 - S1Y5D, D7T5G, T6Y0W — MESSY: each contains a split predecessor (QM7 and/or QJG split at SICBL level —
   e.g. Herts&West Essex 06K/06N→Central East but 07H→Essex; Suffolk&NE Essex 06L/07K→Norfolk&Suffolk but
   06T→Essex). Summing whole predecessors would double-count or misattribute.
 - S0E4D Thames Valley = QU9(whole) + Frimley fragment; S9B9J Surrey & Sussex = QXU+QNX(whole) + Frimley
   fragment — MESSY via the QNQ split (244 LSOAs→TV new SICBL; 95→S&S into 92A; 101→Hants&IoW into D9Y0V).
 - QRL Hants & IoW — RETAINED code, boundary-only gain of Frimley territory.
 RECOMMENDATION (matches user's steer): auto-pool ONLY Z9B2Z (clean). Leave the 5 split/boundary-affected
 new codes (and QRL) as HONEST SHORT SERIES — do NOT fabricate apportioned history. Flag, don't invent.

**3. AUTOMATION FEASIBILITY — strong YES.** The old→new mapping is fully machine-readable from ODS ORD, no
hand-maintenance: each org record carries `Succs.Succ[]` with Type Successor/Predecessor (bidirectional),
`Target.OrgId.extension` (the linked code), `Target.PrimaryRoleId` (org TYPE — RO261=ICB), and a Legal
Date (2026-04-01). `/sync?LastChangeDate=` gives daily deltas. VERIFIED LIVE for all 12+6+QRL today
(Jun-2026; links pre-published from 12-Jan-2026). Splits vs merges are inferable purely from link count +
direction: an old code with >1 Successor = split; a new code whose every predecessor has exactly 1
successor = clean merge. TWO-TIER DESIGN (proposed): TIER 1 auto-pool clean whole-ICB unions (all
predecessors degree-1 → sum, with a reconciliation guard like the existing TF/group gates); TIER 2
detect-and-FLAG any new code touching a split predecessor → fail-loud / escalate to a human decision,
never auto-apportion. AUTO/MANUAL LINE sits exactly at "does any predecessor have >1 successor". CAVEATS:
succession links appear BEFORE operational cutover and never expire → gate the actual series switch on the
old org's Status flipping Inactive / legal-close date, not on link existence; succession is only mandatory
for STATUTORY orgs (ICBs, trusts) — NOT GP practices/sub-ICB, which use RE5 geographic relationships.

**3b. GENERALISATION — CONFIRMED org-type-agnostic.** The same `Succs` mechanism + `PrimaryRoleId` filter
covers NHS Trusts (RO107 etc.) identically; a future trust-merger phase is picked up by changing/loosening
the role filter, NOT by an ICB-only rebuild. Design the pooler around (code, role, succession-links), not
around "ICB". Only excluded tier is non-statutory orgs (GP practices) — out of scope for both dashboards.

**4. UX PROPOSALS (across clean-merge / split / boundary-only):**
 a. POOLED-series transparency alert — reuse the existing break-marker/banner pattern: where a series'
    pre-Apr-2026 portion is reconstructed from predecessors (only Z9B2Z under the recommendation), show a
    marker at the Apr-2026 join + a banner ("history before April 2026 pooled from NHS North Central
    London + NHS North West London"). Honest, consistent with the Feb-2024 / Oct-2023 markers.
 b. Grouped picker — add a "Former ICBs (to Mar 2026)" section beneath current ICBs (mirrors the existing
    Trust/ICB grouped picker). CLEAN merge (Z9B2Z): predecessors QMJ/QRV become ALIASES/redirects to the
    new code (selecting them deep-links to Z9B2Z, since their history now lives there) — avoids a dead
    single-direction stub. SPLIT predecessors (QM7, QJG, QNQ): stay SEPARATELY listed as closed series
    (their history can't be cleanly handed to one successor). New split-derived codes (S1Y5D etc.) stay
    as their own honest short series. QRL: unchanged, stays current.
 c. Directional context notes — selecting any reorganised org shows a contextual "reorganised April 2026"
    note pointing to related codes: Frimley (QNQ) → "split April 2026 between Thames Valley, Surrey &
    Sussex and Hampshire & IoW"; the 3 successors + QRL → "this area was reorganised in April 2026; parts
    came from NHS Frimley ICB — see also …". Drives users between old/new without implying false continuity.

OPEN DECISIONS for the user before any build: (i) confirm auto-pool scope = Z9B2Z only; (ii) approve the
two-tier auto/flag pipeline design + ODS ORD `Succs` as the live source (vs a checked-in mapping file);
(iii) approve the three UX patterns (esp. alias-redirect for clean predecessors vs keep-listed for splits).
Nothing built for Part B.

## 2026-06-20 — BIGGEST DEPLOY: site restructure (waiting-times: /cancer/ + /rtt/ + landing) + RTT goes live (Code)
User approved all three calls (A: rename repo + stub redirect; minimal two-card landing; stub is the
redirect mechanism). Landed as ONE change. Restructure:
 - MOVED the live cancer dashboard from site root to site/cancer/ (index.html, compare.html, data/).
   pipeline/config.SITE_DATA_DIR site/data → site/cancer/data (build_site_data keys everything off it);
   .gitignore + the CI commit paths + the no-op-commit meta.json excludes all repathed.
 - NEW minimal root landing site/index.html (two cards → cancer/ , rtt/).
 - CROSS-LINKS: cancer → ../rtt/ + ../ (All dashboards); rtt → ../cancer/ + ../. Landing → cancer/ , rtt/.
 - REPO RENAME cancer-waiting-times → waiting-times (Pages URL …/cancer-waiting-times/ → …/waiting-times/).
 - STUB redirect repo at the freed-up cancer-waiting-times: index.html + 404.html, JS query+hash+path
   preserving → …/waiting-times/cancer/ (so …/cancer-waiting-times/?org=RJ1 and …/compare.html resolve).
LOCAL VERIFY before deploy: all paths 200 (landing, /cancer/ + compare + data + breakdown, /rtt/ + data +
breakdown); headless render confirms cancer deep-link (?org=&std=&range=&england=) renders + cross-links
(compare.html, ../rtt/, ../), compare.html loads, RTT TF-breakdown renders (../cancer/, ../). 45 tests pass.
Deploy sequence: push (dispatch-only workflow, no auto-deploy) → rename repo → create+enable stub Pages →
workflow_dispatch on waiting-times → watch build+deploy green → verify live.
SHIPPED + VERIFIED LIVE: commit 29dda0c pushed; repo renamed cancer-waiting-times → waiting-times; stub
repo created at the freed name with Pages on (index.html + 404.html). Deploy run 27866606606 GREEN (build
6m2s — cancer + RTT both fetched/built, BOTH gates passed, committed, artifact uploaded; deploy 16s).
Live checks (curl + headless): all paths 200 incl. CI-rebuilt gitignored breakdowns (cancer RJ1.breakdown,
RTT RAJ.breakdown + national.breakdown); live RTT meta shows recon=True, tf maxΔ=0, 642 orgs.
Behavioural: (1) …/cancer-waiting-times/?org=RJ1&std=CMB62 → redirects to …/waiting-times/cancer/?org=RJ1&
std=CMB62 and loads Guy's & St Thomas' (query PRESERVED); (2) …/cancer-waiting-times/compare.html →
…/waiting-times/cancer/compare.html (deep path via 404.html); (3) cancer deep-link renders (CMB62, england=
off); (4) RTT TF-breakdown renders live; (5) landing → cancer/ + rtt/. The daily cron is the SAME workflow,
now running both pipelines with fail-loud gates — this dispatch exercised that path green.
FOLLOW-UP FIX (same session): the first CI run made an "Auto update CWT data" no-op commit (ebe3c1f)
because run.py wrote data_rtt/manifest.json (churning last_checked) every run. Fixed to match cancer —
save the RTT manifest ONLY when a month was actually fetched, so true no-op daily runs leave only the
excluded meta.json files and skip the commit.

## 2026-06-20 — RTT wired into CI (update-data.yml); pipeline runs GREEN end-to-end; DEPLOY HELD for the restructure (Code)
Per the user: wire pipeline_rtt into the existing daily workflow FIRST, do NOT deploy core-only (a live
dashboard with gitignored-and-therefore-dead breakdowns isn't worth a broken interim). Done + validated
locally; the actual Actions-green lands on the held deploy.
NEW MODULES: pipeline_rtt/discover.py (enumerate FY pages 2022-23..current, scrape Full-CSV zip links,
parse month, incremental manifest) + pipeline_rtt/run.py (discover → fetch new/revised → build). Raw
zips stay gitignored + are NOT persisted between CI runs, so each run re-fetches all months (~175MB) and
always picks up NHS revisions — simpler and more correct than an incremental store, no revision-drift to
manage; local re-runs skip unchanged months via the manifest.
FAIL-LOUD-BEFORE-PUBLISH: build.run() reordered so BOTH gates (national SPN headline + sum-of-TFs==C_999)
run BEFORE any file is written; a failure raises, run.py exits 1, the CI step fails, and the deploy job
(needs: build) never runs — so stale/partial RTT data can't ship. Added a dedup guard (_zip_month skips a
second file for an already-processed month). Proven by test_build_fails_loud_and_writes_nothing_on_bad_gate
(build raises AND writes no meta/index/national).
WORKFLOW: renamed to "Update CWT + RTT data and deploy"; added a "Fetch + rebuild RTT" step after the
cancer one; commit step now also stages data_rtt/manifest.json + site/rtt/data (breakdowns gitignored, so
only the core JSON is committed) and excludes BOTH meta.json files from the no-op-commit check. The Pages
artifact uploads the freshly-built site/ — incl. the 642 RTT breakdown files rebuilt in-workspace — so the
live breakdown selector works.
VALIDATED LOCALLY: `python -m pipeline_rtt.run` GREEN against live NHS (scraped 5 FY pages, discovered 49
months, recon=True, TF-sum max|Δ|=0, 642 orgs). 45 tests pass (32 cancer + 13 RTT; new: discover parsing/
FY-enumeration/select-to-fetch, fail-loud-no-publish). YAML valid; artifact contains breakdowns; gitignore
stages core-only. CAN'T get a real Actions run without triggering the (held) deploy, since build→deploy are
coupled — confirmation is local + by-construction until the deploy.
NEXT: restructure plan (cancer-waiting-times→waiting-times, /cancer/ + /rtt/ + root landing) sent for review;
deploy everything (RTT page+core, CI-rebuilt breakdowns, cancer forward-link, restructure) as ONE change.

## 2026-06-19 — RTT polish pass (5 items) applied; RE-RENDERED, AWAITING DEPLOY GO (Code)
Front-end only (site/rtt/index.html) + ONE cancer-page edit (site/index.html), no pipeline/data change.
41 tests still pass; JS --check clean both pages. NOT deployed — paused for the deploy go. The five
user-listed items:
 1. CROSS-LINK both ways: added a forward "RTT Waiting Times Dashboard →" link on the cancer page's
    header (beside Compare), mirroring RTT's "← Cancer" back-link. This edits the DEPLOYED cancer
    index.html but MUST ship in the SAME deploy as /rtt/ (no live link to /rtt/ before it exists).
 2. Dropped the "INCOMPLETE" card eyebrow entirely; the eyebrow now shows the treatment-function name
    when one is sliced, nothing otherwise.
 3. Recovery milestones (65/70%) now drawn ONLY on the all-England, all-TF headline (showMs =
    TF===null && CURRENT.isNational); suppressed on individual-TF and per-provider views, and the
    y-axis no longer stretches to 65/70 off-headline. 92% target line stays on every % view.
 4. Wording aligned to "92% target" everywhere (was "92% standard" on the chart, "92.0% target" on the
    card); decimal dropped via targetPct().
 5. Count cards on <13-month orgs (the 6 parked Apr-2026 ICBs) show "no year-ago data" (neutral) instead
    of a misleading "0% vs yr ago".
RE-RENDERED + state-verified (screenshots/rtt_pol_1..3): England all-TF (milestones present, no eyebrow,
"92% target"), individual-TF (0 milestone lines), NHS Essex 1-month ICB ("no year-ago data"). Tooltip
scale fixed to pass the same showMs so the national dot positions stay correct. NEXT: deploy (the /rtt/
page + data + the cancer forward-link in one go) + CI/cron wiring on the user's go.

## 2026-06-19 — RTT increment 2 BUILT: treatment-function breakdown selector across all 3 measures + TF-sum gate; RENDERED, AWAITING REVIEW (Code)
Decisions from the user applied: keep all five X0x "Other–" buckets separate under an "Other" heading
(23 selectable TFs, default C_999 total); long-waiters = default 52+ with the [52·65·78·104] sub-control
each on its own axis; England overlay %-chart-only; Apr-2026 ICB-reorg parked. BUILT, NOT deployed.
PIPELINE: process_zip now folds C_999 → core store and the 23 individual TFs → a breakdown store;
writes org/<CODE>.breakdown.json + national.breakdown.json (lazy, gitignored, ~9.6MB total, median 6KB).
NEW FAIL-LOUD GATE reconcile_tf: sum across the 23 TFs == published C_999 total for EVERY org-month
BEFORE any file is written — 24,776 org-months reconcile EXACTLY (max|Δ|=0, same discipline as cancer's
cancer-group gate). meta.json gains treatment_functions[] (code/name/group, X0x→"Other") + tf_reconciliation.
Build ~2min over 49 months. National SPN gate still green.
FRONT END: a grouped "Treatment function" dropdown (Overview→All / Specialty / Other — same picker
pattern as the org list) in the filterbar, DRIVES ALL THREE measures (cards + chart). Default All
treatment functions = the core C_999 series. Selecting a TF lazy-loads the breakdown (national too, for
the matched England overlay). Series accessors generalised over a {months,measures} source (breakdown
omits data_status/target — defaulted). Low-reliability (n<10) now MEANINGFUL at TF level and rendered:
open-square markers + lighter-teal dotted segments + legend entry (verified live on KIMS Hospital
ophthalmology, 6 square markers). Empty state for a TF an org doesn't publish (cards + chart explain
the gap; measure toggle still works). Export filename includes the TF. Title/cards carry the TF name.
VERIFIED (screenshots/rtt_bd_*): RAJ Trauma & Orthopaedic across all 3 measures (33.0% / 16.1k / 2.58k),
England-overlay matched to the TF, low-reliability squares, grouped dropdown, empty-TF case, export name.
41 tests pass (32 cancer + 9 RTT; new: breakdown routing, TF-sum gate pass/fail, build_tf_payload).
STILL NOT done (per build order): polish, deploy, CI workflow + daily cron. Next: the dashboard is now
functionally complete (picker + 3 measures + 2 chart types + TF breakdown + reuse mechanics) — remaining
is polish + deploy/CI when the user calls it.

## 2026-06-19 — RTT increment 1 BUILT: pipeline + /rtt/ page (picker, % chart, 3-measure toggle, counts chart); RENDERED, AWAITING REVIEW (Code)
Architecture calls all made by the user (entry below). BUILT this increment, NOT deployed — paused
for review per the build order. New, parallel to the cancer stack: `pipeline_rtt/` (config + build),
`tests_rtt/` (6 tests), `site/rtt/index.html` + `site/rtt/data/`. Full suite 38 pass (32 cancer + 6
RTT). data_rtt/raw/*.zip gitignored (175MB, re-fetched); the ~2MB derived per-org JSON is committed.
PIPELINE: scraped all 49 monthly Full-CSV zips (Apr-2022→Apr-2026) off the FY sub-pages; stream-parse
each, keep ONLY Part_2 (incomplete) / C_999 (all-TF) rows, exclude NONC, derive 6 metrics/org-month
from the 105 bands. Aggregates: national = all non-NONC rows; provider = by Provider Org Code (across
commissioners); icb = by Commissioner Parent. Output 642 orgs (594 providers [96 hidden negligible],
48 ICBs) + national; org JSON median 3.5KB, total 1.9MB.
RECONCILIATION GATE PASSES (fail-loud, Apr-2025 vs SPN): pct18=0.5973 (SPN 59.7% ✓), waitlist
7,389,065 (~7.4M ✓), w78=1,361 ✓ exact, w104=171 ✓ exact; w52=190,023 vs 190,068 and w65=9,244 vs
9,258 within the 1% count tolerance (revised-extract vs original-SPN vintage). The `unknown clock
start` column is 0 throughout and `Total All` == sum of bands exactly, so the denominator question is
moot — confirmed empirically, no need to chase the rules-suite wording.
FRONT END (reuses cancer's CSS, picker, range/expand/export/England mechanics verbatim): three
summary cards ARE the measure toggle [% within 18 weeks · Waiting-list size · Long waiters]; the %
card shows vs-92%, the count cards show latest + YoY trend (no target). TWO chart renderers — the
% chart is the cancer CMB model (0–1, 92% target line + faint 65%/70% recovery-milestone reference
lines in the right margin, England grey overlay) and a NEW count chart (numeric auto-scaling 0-based
axis, K/M ticks, no target). Feb-2024 break marker + banner on ALL measures (the cancer Oct-2023
logic, shown only when the window reaches pre-break). Headless render verified all paths
(screenshots/rtt_*): measure toggle, threshold sub-control, England-overlay scoping, break marker,
PNG/SVG export.
TWO calls made in-build, flagged for the user to confirm/redirect:
 1. LONG-WAITERS proposal = default 52+, with a [52·65·78·104 wks] segmented sub-control, each
    threshold on its OWN auto-scaled axis (rejected: all four on one linear axis — 52+ tops ~500k
    while 104+ tops ~20k, so 104+/78+ would be a flat line on the floor; the sweep screenshots show
    each is only readable on its own scale). Open to a log-axis overlay or small-multiples instead.
 2. ENGLAND comparison overlay is shown on the % chart ONLY (counts can't share a linear scale with
    the 7M national total); the toggle is hidden for the two count measures. Could revisit with a
    dual-axis or %-of-England framing.
KNOWN, noted not blocked: an Apr-2026 ICB reorganisation introduces 6 new merged ICB codes (NHS
Essex, Surrey & Sussex, Thames Valley, etc.) appearing only in the latest month — honest single-point
series; could hide no-recent-data ICBs in a polish pass. Provider negligible-hide threshold (recent
12-mo peak waitlist < 100) is a placeholder; 498 providers remain selectable (searchable picker).
NOT YET (per build order): TF breakdown selector (the 24-value taxonomy — shown to the user for the
collapse-X0x decision before wiring), polish, deploy, CI workflow, daily cron.

## 2026-06-19 — INVESTIGATION: second dashboard for RTT (Referral to Treatment) waiting times at /rtt/ (Code; user makes the architecture calls)
INVESTIGATE-ONLY, nothing built (same discipline as the time-range / org-hiding investigations).
Source: england.nhs.uk RTT, per-FY sub-pages (rtt-data-2025-26 etc.). Verified against the LIVE
Mar-2026 file listing + the Apr-2025 SPN (downloaded + parsed the actual Mar-2026 Full CSV extract).
Scope = % within 18 weeks (92% standard) AND waiting-list size + 52/65/78+ long-waiters — ALL of
which are INCOMPLETE-pathway metrics, so the whole stated scope comes from ONE pathway type
(Part_2). NHS's own dashboard at data.england.nhs.uk/dashboard/rtt — context only, nothing to do.

DATA MODEL. Each month publishes NINE files: 4 provider XLSX + 4 commissioner XLSX (Incomplete /
Admitted / NonAdmitted / NewPeriods) + ONE combined **Full CSV data file** (ZIP ~4M → one ~85MB
CSV, 121 cols). BOTH provider AND commissioner are published; commissioner aggregates sub-ICB → ICB
→ region → England. Use the Full CSV (the RTT analogue of cancer's "Monthly Combined CSV") — it
holds all 5 pathway types + both org levels in one, so we DON'T need the XLSX parser. Pathway types
(col "RTT Part Type"): Part_1A completed-admitted, Part_1B completed-non-admitted, Part_2 incomplete,
Part_2A incomplete-with-DTA, Part_3 new-clock-starts. Our scope needs only **Part_2**.
- Dimensions: provider/commissioner org+parent codes (cols 1–13), **Treatment Function** (a reduced
  24-value taxonomy: C_100 General Surgery … C_502 Gynaecology + X02–X06 "Other" + C_999 a
  pre-aggregated Total — codes carry a `C_` prefix), and **105 one-week wait-band columns**
  ("Gt 00 To 01 Weeks" … "Gt 103 To 104 Weeks" + a single "Gt 104 Weeks" catch-all), then Total /
  unknown-clock-start / Total All summary cols.
- CAVEAT (confirmed by parsing the file): in the Full CSV the Total + unknown-clock-start summary
  cols are BLANK — we compute every metric from the 105 bands ourselves. Must (a) filter out NONC
  (non-English-commissioned) rows — present only in the Full CSV, will over-count headline if kept;
  (b) NOT double-count C_999 (the all-TF total row) against the individual TFs.
- DERIVATION: waiting-list size = sum of all 105 bands for Part_2 (= the "size of the RTT waiting
  list"). % within 18 weeks = sum(first 18 bands) / denominator. 52+/65+/78+/104+ = sum of bands
  from that threshold on (104+ = the single catch-all band). DENOMINATOR caveat: the established
  published convention is to EXCLUDE unknown-clock-start from the % (reported as a separate count)
  while the headline waiting-list size (7.4m, Apr-25) is the grand total INCLUDING them — but the
  exact wording isn't printed in the v5.0 guidance / SPN I could decode. RESOLUTION (matches our
  existing reconcile-to-total gate discipline): compute it, then RECONCILE the derived national %
  to the published SPN headline (Apr-25 = 59.7%) as a fail-loud build gate rather than trusting the
  prose. Same for the long-waiter counts (190,068 >52wk / 9,258 >65wk / 1,361 >78wk / 171 >104wk).

DISCONTINUITIES. (1) The 92% / 18-week incomplete standard IS still the live NHS Constitution
standard in 2025/26 (the admitted-90% / non-admitted-95% measures were ABOLISHED Oct-2015, leaving
the single incomplete measure — so any pre-Oct-2015 series is a separate regime, like cancer's
Oct-2023). (2) **Feb-2024 community-services break** — community paediatrics + other community
pathways left RTT for the CHS waiting-list collection (~36k pathways dropped Feb-24, ~7k more Mar-24;
est. ~4.4k fewer 52wk / ~2.5k 65wk / ~1.4k 78wk). This is the direct analogue of cancer's Oct-2023
break and needs the same "series changed" marker/banner treatment. (3) Apr-2021 DCB0095 return
change; CCG→ICB transition Jul-2022 (commissioner identifiers change); COVID Apr-2020 cliff (~47%);
some periods have non-submitting trusts (NHS publishes "incl. estimates"; medians/percentiles do
NOT include estimates). RECOVERY TRAJECTORY (planning guidance / elective-reform plan) gives
MILESTONE lines distinct from the flat 92% target: 65% by Mar-2026 (+ every trust ≥5pp), 70% by
Mar-2027, back to 92% by Mar-2029 — candidate annotations.

REUSABILITY. Drops in AS-IS (all front-end-only, chart-agnostic mechanics that read what's on
screen): the grouped Trust/ICB picker + index.json model (RTT has both levels, classifies the same
way), one-JSON-per-org load + lazy per-org breakdown file, time-range presets, expand modal,
PNG/SVG export, Show-England toggle, low-reliability (n<10) flag, provisional/final markers, the
discover→normalise→build_site_data pipeline scaffold + reconciliation-gate + CI pattern. The
**% within 18 weeks** chart is essentially cancer's CMB model (a 0–1 performance series + a single %
target line) — near drop-in. GENUINELY NEW: (a) a **counts / absolute-number chart** — numeric
auto-scaled y-axis (K/M formatting, no 0–1 cap, no single % target) for waiting-list size + the
52/65/78/104+ long-waiter family (multi-series); bigSVG/sparkSVG + bigScales assume performance 0–1,
so a numeric-axis variant is the real new component (the SVG scaffold/range/expand/export/tooltips
around it are reused). (b) the **24-treatment-function taxonomy** replaces the cancer-group selector
as the shared "specialty" lens — SIMPLER than cancer (single dim, no route×modality cross). (c) a
**measure/pathway toggle** to fill the slot cancer's 3-standard toggle held: [% within 18 weeks] vs
[Waiting-list size] vs [Long waiters 52/65/78+], the first on the % chart, the rest on the new counts
chart. (d) Feb-2024 break marker + recovery-milestone lines. (Completed-admitted / non-admitted
median + 92nd-pctile waits are OUT of the stated scope — a possible later extension, not this round.)

SIZE / PERF. The one-JSON-per-org model HOLDS — do NOT ship the 105 raw bands to the browser;
pre-aggregate in the pipeline to ~6 derived metrics per org-month-TF (pct18, waiting-list, w52, w65,
w78, w104). Est. payloads: core (all-TF C_999 row) ~8–10KB/org for 48mo (~30KB full history since
2012); lazy per-org breakdown (24 TFs × 6 metrics × months) ~36KB (48mo) to ~130KB (full) — same
order as today's cancer breakdown files (40–200KB), lazy-loaded one at a time. Org cardinality
similar (~185 acute providers + 42 ICBs + ~106 sub-ICBs + regions). The ONE place the cancer model
needs a guard: if a 105-band DISTRIBUTION histogram chart is ever wanted, that's ~125k numbers/org —
ship only the latest-month (or a few snapshot months) bands or load on demand, never the full
band×month×TF cube. PIPELINE adaptation: unlike cancer's per-FY combined CSV, the RTT Full CSV is
PER-MONTH (~85MB each) — a from-scratch pull of full history is ~14GB of raw, so stream-filter to
Part_2 + derived metrics into a tidy parquet and do NOT hoard raw monthly fulls the way data/raw
keeps the cancer FY files (the daily incremental fetch only ever adds the newest month).

OPEN ARCHITECTURE CALLS handed to the user (none made here): chart-type set + whether to build the
counts chart now; how the measure/pathway toggle maps; treatment-function taxonomy grouping (24 as-is
vs collapse the X0x "Other" set); history depth (since 2012 vs a bounded window); whether to confirm
the exact % denominator via the rules suite or lean on the reconcile-to-headline gate.

## 2026-06-16 — v16 SHIPPED; VERIFIED LIVE (Code)
"Show England" toggle approved and shipped: commit 1ba5298 (site/index.html + DECISIONS.md — no
pipeline/data change) via watched workflow_dispatch run 27620549350 — build (3m0s: tests → fetch
→ rebuild → upload) and deploy (16s) both GREEN; data-commit a no-op so master stayed at 1ba5298.
VERIFIED LIVE: index/compare/data all 200; served index.html carries the toggle (SHOW_ENGLAND,
id="engchk", setShowEngland, syncEnglandUI, ?england=off hook). Headless render of the live site
confirms production behaviour: provider England ON (natPath=1, legend+export have England, toggle
checked) → OFF (natPath=0, England gone from legend AND export, toggle unchecked); England tab
(no separate comparison line, toggle hidden, org's own "England" line only). The entry below is
the build history; this marks it shipped.

## 2026-06-16 — v16: SHOW/HIDE England comparison line; RENDERED, AWAITING DEPLOY GO (Code)
Front-end only (site/index.html), no pipeline/data change. JS node --check clean. NOT DEPLOYED —
paused for review. A "Show England" checkbox in the chart filter row (alongside referral route /
time range), DEFAULT ON. New state SHOW_ENGLAND; one switch drives every surface because it just
gates ACTIVE_NAT in renderBig — `ACTIVE_NAT = (SHOW_ENGLAND && !isNational && nat…) ? nat : null`
— so OFF drops the grey line, its legend entry AND its pull on the y-scale, and the export (keys
off ACTIVE_NAT) + expand modal (read the on-screen chart) hide it too. SCOPE: providers +
commissioners only — on the England tab the org's own line IS England, so syncEnglandUI() HIDES
the toggle there (engwrap.hidden = CURRENT.isNational). Persists across org/standard switches like
RANGE. Deep-link hook ?england=off (consistent with ?range=). CSS overrides the global
uppercase/block `label` defaults for the inline toggle.
Verified (screenshots/v16_*): provider England shown (natPath=1, legend has England, toggle
checked) vs hidden (natPath=0, no England in legend, org/target/marker/axis intact); England tab
(toggle hidden, org's own "England" line only, no separate comparison line); export with England
hidden (no "England" anywhere in the SVG, composes with the 3y window + title-cased subtitle).

## 2026-06-16 — v15 SHIPPED in one deploy; VERIFIED LIVE (Code)
All three (time-range + expand modal + image export) approved and shipped together: commit
3e59a8e (site/index.html + DECISIONS.md + STATUS.md + .gitignore — no pipeline/data change) via
watched workflow_dispatch run 27619479528 — build (3m8s: tests → fetch → rebuild → upload) and
deploy (25s) both GREEN; data-commit step a no-op so master stayed at 3e59a8e. Pre-deploy,
FDS28 confirmed clean (no Oct-2023 marker in 3y/12mo/All, banner correctly hidden — the marker
is standard-guarded `CURRENT_STD!=="FDS28"`, not just window-based; screenshots/v15_h).
VERIFIED LIVE: index/compare/data all 200; served index.html carries every new marker
(RANGE_MONTHS, firstVisibleMonth, data-range="3y", buildExportSVG, #chartmodal, humanName).
Headless render of the live site confirms production behaviour: CMB62 default = 3y window
(first visible 2023-04, marker shown, banner shown), CMB62 12mo (first visible 2025-04, marker
ABSENT, banner shown), FDS28 All (first visible 2022-04 pre-break, marker ABSENT, banner
hidden). The two entries below remain the build history; this marks them shipped.

## 2026-06-16 — v15: TIME-RANGE control added; all THREE (range + expand + export) RENDERED, AWAITING DEPLOY GO (Code)
Front-end only (site/index.html + .gitignore), no pipeline/data change. JS node --check clean.
NOT DEPLOYED — paused for review of the four renders below; user pre-approved deploying all
three together once happy. #1 design chosen by the user (overrides the investigation's
"Since Oct 2023" recommendation):
- **Fixed ROLLING window** (constant chart width as data accrues), presets [3 years · 12 months
  · All] as a segmented control right-aligned in the filterbar. DEFAULT = 3 years (36 months),
  applied to ALL standards incl. FDS28 (NOT standard-aware — simpler). Display-only: clips the
  big chart's org + England series (England clipped to the org's first visible month so they
  align and the y-scale isn't pulled by out-of-window points); the cards' recent-trend
  sparklines are untouched. State: RANGE + RANGE_MONTHS, firstVisibleMonth()/clipSeries();
  deep-link/render hook ?range=3y|12m|all.
- **Adaptive x-axis labels**: step = ceil(n/8) targeting ~8–10 labels, last month always
  labelled (loop stops short to avoid collision) — fixes both sparse-on-short and dense-on-long.
- **Oct-2023 marker rule**: in-chart dashed line + label shown ONLY when xs[0] < comparability_
  break (visible window includes PRE-break data). Once the rolling window clears Oct-2023
  (~2027) the marker disappears entirely — no line, no label, no edge-note — since all visible
  data is comparable and the banner below the chart still carries the note. "All" always shows
  it in place; today's 3y default still shows it (reaches ~Apr 2023). Verified: 3y→present,
  All→present, 12m→absent + banner still shown (screenshots/v15_d/e/f).
- **#2/#3 now respect the window**: export/expand read the on-screen chart, so they capture the
  SELECTED range automatically (12m export sample = Apr 2025→Mar 2026, no marker —
  screenshots/v15_export_12m.*). Export SUBTITLE now title-cased via humanName() (Airedale NHS
  Foundation Trust), matching the filename; the on-page .tag stays as-published.
Renders for review: v15_d_default_3y_marker, v15_e_all_marker, v15_f_12m_no_marker,
v15_g_expanded_range, v15_export_12m.{png,svg}.

## 2026-06-16 — v15: per-org chart EXPAND modal + image DOWNLOAD (PNG/SVG); RENDERED, AWAITING REVIEW (Code)
Front-end only (site/index.html + .gitignore), no pipeline/data change. JS node --check
clean. NOT DEPLOYED — held for review. Two builds + one investigation (below).
(1) **Expand:** a toolbar in the chart title row (`.charttools` in `.ttl`) with Expand +
Download. Expand MOVES the live `#bigpanel` node into a fullscreen overlay (`#chartmodal`)
and restores it on close — so route/modality dropdowns, tooltips, legend and the download
control are the SAME nodes and keep working with zero duplicated IDs / re-wiring (verified:
group-aware route dropdown opens + filters inside the modal — screenshots/v15_c). Close via
✕, Esc, or backdrop click; `?expand=open` render hook added (mirrors `?panel=open`). Needed
adding `id="bigpanel"` (panel had only the class).
(2) **Download PNG/SVG:** `buildExportSVG()` composes a SELF-CONTAINED svg = header strip
(title + organisation + flat-SVG legend) ABOVE the on-screen chart body (taken from
`#chartbox svg` innerHTML, so the export is EXACTLY what's displayed — current group/route/
modality slice, all marker states, the header-strip "standards changed" annotation, the
right-margin "target NN.N%" label, the axis). `var(--x)` resolved to literals via
`getComputedStyle` (canvas rasterisation ignores page :root vars) + explicit font-family
(serif title, mono chart). SVG = blob save; PNG = rasterise that svg to a 2× canvas → toBlob.
Filename `humanName(org)-STD-group[-route][-mod].ext`, e.g.
`Airedale-NHS-Foundation-Trust-CMB62-Haematology.png` (humanName title-cases the ALL-CAPS NHS
name, preserving NHS/FT/ICB acronyms). Sample PNG + SVG rendered (screenshots/v15_export_*).
Both controls live inside `#bigpanel` so they work identically inline and expanded; export
reads live state so it's view-independent.
DEPENDENCY: export/expand capture WHAT'S ON SCREEN; once a time-range control (#1) exists they
should respect the selected window — for now they capture the current FULL series.

## 2026-06-16 — INVESTIGATION: time-range control for the per-org chart (Code; user to choose window)
Report only, nothing built. Chart is 48 months now (Apr 2022 → Mar 2026), grows ~1/month.
Findings: (a) x-axis labels (every 6mo + last → 9 now, ~89px apart) are fine today but the
fixed step gets too sparse on short windows and too dense past ~7yr — recommend an ADAPTIVE
step targeting ~8–10 labels. (b) The real crowding is the DATA POINTS: ~17px apart now, and
the 11px tooltip hit-circles already overlap (<22px) — a windowed default helps more than label
thinning. (c) Recommended control: presets [Since Oct 2023 (default) · Last 12 months · All];
the "Since standards changed" default anchors the Oct-2023 marker at the LEFT EDGE (always
visible, comparable data only, grows gracefully) and revives the original 2023-10-default
decision relaxed in v7. For FDS28 (no break) the default is All/Last-N. If instead a short
rolling window that EXCLUDES the break is chosen, the in-chart vertical marker must degrade to
a left-edge "← standards changed earlier" note (nothing to point at). Full write-up handed to
the user; window choice deferred to them.

## 2026-06-15 — CHART-POLISH SERIES (v10–v14) SHIPPED in one deploy; VERIFIED LIVE (Code)
All THIRTEEN front-end changes from the five v10–v14 entries below (each previously
"RENDERED, AWAITING REVIEW") were approved and bundled into ONE commit (ab9b8fc,
site/index.html + DECISIONS.md only — no pipeline/data change) and shipped via a single
watched workflow_dispatch: run 27560316331 — build (3m16s: tests → fetch no-op → rebuild →
deploy) and deploy both GREEN. The build's data-commit step was a no-op (only meta.json
built_at would change, which CI skips), so master stayed at ab9b8fc.
VERIFIED LIVE: index/compare/data all 200; the served index.html carries every new marker
(one-line legend w/ "|" boundary + lgbar, "low reliability (n<10)", P.r:76 right margin,
header-strip "standards changed", sparkline `unc` provisional-OR-low check, dotted
low-reliability dash "1.5 3"); the removed dead sliceLabel() is gone. Headless render of the
live Airedale Haematology Consultant Upgrade CMB62 breakdown confirms the chart renders
correctly in production: title "— Haematology", legend order "this organisation · low
reliability (n<10) · provisional | England · target", open-square(dotted)/open-circle(dashed)
markers both in the lighter teal, solid-grey England line, "standards changed" in the strip,
"target 85.0%" in the right margin, and the three card sparklines matching the chart's colour
logic (screenshots/v14_LIVE_airedale + _crop). The five entries below remain the per-change
build history; this entry marks them all shipped.

## 2026-06-15 — v14 VISUAL: legend reorder (low-rel before provisional) + sparkline colour consistency; RENDERED, AWAITING REVIEW (Code)
Front-end only (site/index.html), no pipeline/data change. 32 tests pass; JS node --check
clean. NOT DEPLOYED — held for user sign-off, then ALL THIRTEEN changes (v10+v11+v12+v13+these
two) ship together in ONE watched deploy. Two changes:
1. LEGEND ORDER: low-reliability now BEFORE provisional. New line is "this organisation ·
   low reliability (n<10) · provisional | England · target" (orgGroup array reordered to
   [org_, low_?, prov_]). Display-order only; the draw-time PRECEDENCE is unchanged and still
   correct (provisional wins when a point is both — a separate semantic from list order).
2. SPARKLINES brought in line with the main chart's COLOUR logic. Previously the card
   sparklines only de-emphasised low-n months (lighter teal); provisional-but-not-low months
   were drawn strong solid teal — inconsistent with the main chart, where provisional is also
   lighter teal. Added a data_status check: a segment is now uncertain (lighter teal --org-muted
   + dashed) if EITHER endpoint is low-n OR provisional; final/normal stays strong solid teal.
   COLOUR ONLY — no circle/square markers added (sparklines carry none; too small), per the
   user. DELIBERATELY KEPT: the latest-point dot semantics (amber when latest is below target,
   teal when it meets, hollow muted ring when low-n) — the below-target amber cue is the dot's
   purpose and the latest month is almost always provisional, so muting it would gut the cards'
   at-a-glance signal; the change is scoped to the trend LINE colour as asked.
Renders: screenshots/v14_a_airedale_hard_case(.png) + _legend_crop (legend in the new order:
low-reliability before provisional) + _cards_crop (all three card sparklines now show strong
solid teal for final months and lighter-teal dashed for provisional/low-n, with the amber/teal
latest-dot cue preserved). Stress-test chart (v13) unaffected by the reorder; full page intact.

## 2026-06-15 — v13 VISUAL: one-line legend + same-colour uncertain states (shape/dash only); RENDERED, AWAITING REVIEW (Code)
Front-end only (site/index.html), no pipeline/data change. 32 tests pass; JS node --check
clean. NOT DEPLOYED — held for user sign-off, then ALL ELEVEN changes (v10+v11+v12+these two)
ship together in ONE watched deploy. Two changes:
1. ONE-LINE LEGEND (replaced v12's two-row layout). Single flex row, wraps gracefully on
   narrow widths: "this organisation · provisional · low reliability (n<10) | England ·
   target" — middot separators within groups, a "|" marking the boundary between the org
   series + its uncertain states and the reference lines. CSS .legend back to flex-wrap row;
   added .lgitem/.lgsep/.lgbar; dropped the v12 .lgrow/.lg-org/.lg-states/.lg-div classes.
2. BOTH UNCERTAIN STATES NOW THE SAME LIGHTER TEAL (--org-muted), distinguished ONLY by shape
   + dash: provisional = open CIRCLE + DASHED (6 4); low-reliability (n<10) = open SQUARE +
   DOTTED (1.5 3). Normal/final unchanged (strong solid --org + filled circle). Both uncertain
   lines now share stroke-width 1.8 / opacity 0.9 and the muted colour, so weight/colour no
   longer differ — shape + dash carry the whole distinction; both read as equally de-emphasised
   vs final. Provisional marker outline changed --org→--org-muted (low-rel was already muted).
   Low-reliability caption "dashed"→"dotted, lighter-teal".
   SCOPE: main chart + its legend only; the top summary-card sparklines were not in scope and
   are unchanged (no legend there; de-emphasised summaries) — conscious, flagged here.
VERIFIED on re-render (the stress test, a mostly-uncertain series): screenshots/
v13_a_airedale_hard_case(.png + _crop) — Airedale Haematology Consultant Upgrade CMB62. With
both uncertain states the same colour, circle-vs-square + dashed-vs-dotted still tell them
apart clearly even where points are dense (mid run of dotted squares vs right-side dashed
circles); England solid grey + target margin label + one-line legend all intact. Full page
confirms cards/banner/footer intact.

## 2026-06-15 — v12 VISUAL: target-label in margin + legend restructure + distinct markers/precedence; RENDERED, AWAITING REVIEW (Code)
Front-end only (site/index.html), no pipeline/data change. 32 tests pass; JS node --check
clean. NOT DEPLOYED — held for user sign-off, then ALL NINE changes (v10 + v11 + these three)
ship together in ONE watched deploy. Three changes:
A. TARGET LABEL moved into the RIGHT MARGIN (primary option, used — it fit). BG.P.r 16→76
   reserves a right gutter (same principle as the v11 "standards changed" header strip); the
   "target NN.N%" label sits there level with the target line (y=ty, right-aligned to the SVG
   edge), so it no longer covers the org/England series. Dropped the v11 faint plate (no data
   in the margin, so none needed). Did NOT need the below-the-line or revert fallbacks.
B. LEGEND RESTRUCTURED into an org cluster + reference row. Row 1: "this organisation" (solid
   teal, filled marker) as PRIMARY, with "provisional" and "low reliability (n<10)" as
   visually-subordinate states (lg-states: smaller font, opacity .62) grouped tight to it;
   lg-org is flex-wrap:nowrap so the cluster never breaks mid-group. Thin divider (lg-div,
   align-self:stretch over a width:max-content legend, so it spans exactly the widest row).
   Row 2 (reference): "England" (solid grey) + "target" (dashed amber). Label kept as "this
   organisation" (stable width), not the real org name. legendSwatch gained a 3rd arg for a
   SQUARE marker.
C. DISTINCT MARKERS + PRECEDENCE. Markers are now shape-distinct (legible against solid-grey
   England even when the whole series is one state): provisional = open CIRCLE, low-reliability
   = open SQUARE, normal-final = filled circle. Per-point state is MUTUALLY EXCLUSIVE with
   PROVISIONAL WINNING: a point that is both provisional AND n<10 renders as provisional
   (circle); the square means specifically "final but n<10". The line-segment precedence was
   flipped to match (provEdge before lowEdge) so segments and markers agree. Low-reliability
   caption reworded (open squares; "months also provisional show as provisional instead").
   As predicted, the Airedale recent both-states points flip from low-reliability to
   provisional styling — correct, not a regression.
Renders: screenshots/v12_a_airedale_hard_case(.png + _crop) — the named hard case showing ALL
of it: grouped two-row legend w/ divider, circle (provisional) vs square (low-final) markers
with precedence applied (recent both-states = circles), "target 85.0%" in the right margin
clear of the series; plus v10/v11 (solid-grey England, title "— Haematology", no hint,
"standards changed" in strip). Spot-check screenshots/v12_b_spotcheck_nottingham(_crop) — RX1
Urology Consultant Upgrade CMB62 (mixed: 40 normal-filled, 2 squares, 6 circles, with a
comparison line): the series crosses the target line repeatedly yet "target 85.0%" stays
legible in the margin; no new collision. Full page v12_a confirms cards/banner/footer intact.

## 2026-06-15 — v11 VISUAL: hint removal + title simplification + chart-annotation declutter; RENDERED, AWAITING REVIEW (Code)
Front-end only (site/index.html), no pipeline/data change. 32 tests pass; JS node --check
clean. NOT DEPLOYED — held for user sign-off on change #6, then the WHOLE bundle (these three
+ the v10 three: trimmed→now-removed hint, decluttered legend, solid-grey England line) ships
in ONE watched deploy. Three changes:
4. GROUP hint beside the referral-route box REMOVED entirely (#slicehint). Last round it was
   trimmed to "<group> group"; now gone — redundant with the chart title. FDS28's "Route and
   treatment-modality breakdowns aren't published for the 28-day standard." line KEPT.
5. Chart title (#bigttl) simplified: now `<standard label> — <cancer group>`, ALWAYS showing
   the group incl. "All cancers" (was: group omitted for All cancers, and route/modality
   appended). Route/modality dropped from the title — they're read from their own dropdowns.
   Reuses groupText(); removed the now-dead sliceLabel() fn and the sliceOn local.
6. Chart annotations moved OUT of the plotted data region (they collided with the series —
   e.g. Airedale Haematology CMB62: "standards changed" floated at ~100% where the dotted
   series weaves, "target 85.0%" sat on the target line where the series crosses). FIX, chosen
   so it holds for ANY chart (data position varies), not just the empty spot here:
   - Added a header strip above the plot: BG.P.t 16→36. The y-scale maps the highest value to
     y=P.t, so the band y<P.t is GUARANTEED empty of data on every chart. "standards changed"
     now sits in that strip, centred over its rule (x clamped off both edges), with the rule
     extended up to meet it. Never overlaps the series.
   - "target NN.N%" label given a faint panel-coloured plate (rect, var(--panel), opacity 0.82,
     rounded) behind it, right-aligned just above the target line — legible wherever the series
     crosses, since the full-width target line has no reliably-empty spot.
Renders: screenshots/v11_a_airedale_hard_case(.png + _crop) — the named hard case: title
"— Haematology", no route-box hint, "standards changed" up in the strip clear of the dotted
series, "target 85.0%" on its plate where the series crosses it; solid-grey England + decluttered
legend (v10) also visible. Spot-check screenshots/v11_b_spotcheck_england_cmb31(_crop) —
England 31-day all-cancers: title "— All cancers" (group shown for all-cancers), "standards
changed" cleanly in the strip, "target 96.0%" on its plate; no new collision. Full page
v11_a confirms cards/banner/footer intact.

## 2026-06-15 — v10 VISUAL: hint trim + legend declutter + provisional/England line fix; RENDERED, AWAITING REVIEW (Code)
Front-end only (site/index.html), no pipeline/data change. 32 tests pass; JS node --check
clean. NOT DEPLOYED — held for user sign-off on change #3 before it ships (their request).
Three changes:
1. GROUP-selected hint trimmed: "<group> group · narrow by referral route, or change the
   group above." → just "<group> group" (#slicehint, line 606). FDS28's "Route and
   treatment-modality breakdowns aren't published for the 28-day standard." line KEPT as-is.
2. Legend decluttered to organisation-only: "England · <group> · <route>" → "England";
   "this organisation · <group> · <route>" → "this organisation". Dropped the ${sliceTag}
   interpolation from both the org and England legend entries (and removed its now-unused
   const). The group/route/modality is already named in the chart title (#bigttl), so the
   legend was redundant and wrapped onto a second line. provisional/target/low-reliability
   legend items unchanged.
3. PROVISIONAL-vs-ENGLAND legibility fix. Root cause: "dashed" meant BOTH "provisional"
   (lighter teal, on the org line) AND "the England comparison line" (grey) — so on a
   mostly-dashed org series the two dashed lines were near-indistinguishable. FIX: made the
   England comparison line a faint SOLID grey line (stroke var(--nat), width 1.6, opacity
   0.85; dropped stroke-dasharray="3 3") in BOTH the chart (bigSVG natpath) and the matching
   legend swatch. "Dashed" is now reserved for the org series' own states (provisional =
   lighter teal dashed; low-reliability n<10 = muted teal dashed). Solid grey vs dashed teal
   separates them by both colour AND dash even on a heavily-provisional/low-n org.
Hard case re-rendered for confirmation: Airedale (RCF) → Haematology → Consultant Upgrade,
CMB62 — the case the user named. (Note: this slice's monthly totals are all n<10, so its line
is low-reliability dashed teal rather than provisional dashed; the England-collision and the
fix are identical either way.) Renders: screenshots/v10_a_hint_trimmed (trimmed hint +
decluttered legend on the all-routes Haematology view), v10_b_legend_and_line_AFTER (hard
case, full page), v10_b_crop_BEFORE vs v10_b_crop_AFTER (chart crops — BEFORE: grey-dashed
England weaving through the dashed teal org line; AFTER: solid grey England clearly separable).

## 2026-06-15 — v9 VISUAL: index gap fix + "Beta" relabels across both pages; DEPLOYED (Code)
Front-end only (site/index.html + site/compare.html), no pipeline/data change. 32 tests
pass; JS node --check clean on both pages. Four changes:
1. INDEX gap regression FIXED. The v8 .orgrow row left a blank line on the England view
   (no org dropdown there): the empty inline-block byline still generated a line box.
   Added `.orgname:empty{display:none}` so an empty byline (England, or a region-less
   provider) generates no box and .orgrow collapses to zero height — spacing back to
   pre-v8. Providers/Commissioners unaffected (dropdown present).
2. INDEX cross-link relabelled "Compare trusts →" → "Compare Providers (Beta) →" (matches
   the comparison page's actual scope + the Providers tab; "(Beta)" flags WIP). Label only;
   href unchanged.
3. COMPARE <h1> AND browser <title> → "NHS Cancer Waiting Times Dashboard" (matched the
   per-org page, which uses that string for both; the old title was "Trust comparison —
   Cancer Waiting Times Explorer", stale branding — updated both for consistency).
4. COMPARE subtitle → "England · how providers compare (beta version)" (source lower-case;
   .sub has text-transform:uppercase so it renders "ENGLAND · HOW PROVIDERS COMPARE (BETA
   VERSION)"). The user's quoted current text matched the actual source (caps are CSS) —
   no discrepancy to flag.
Renders: screenshots/v9_a_index_gap_closed (England: buttons → Cancer group, no blank row;
"Compare Providers (Beta) →" link), v9_b_compare_header (new title + subtitle). DEPLOYED
standalone & VERIFIED LIVE: run 27548485696 (workflow_dispatch) — build + deploy both
GREEN. Live: both pages 200; index has "Compare Providers (Beta) →" + the
.orgname:empty rule (old "Compare trusts" gone); compare h1 + <title> = "NHS Cancer
Waiting Times Dashboard" and subtitle "how providers compare (beta version)" (old
"Trust comparison" / "how trusts compare" gone).

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
