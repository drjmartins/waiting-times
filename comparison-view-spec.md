# Spec: Trust comparison view (v1, regions-only)

Source: planning session. Hand to Claude Code as a build instruction. Per the
working agreement, the WHAT and the methods rules below are settled (planning
session's call); HOW to implement them in the pipeline and front end is Code's
call. Anything marked "open for Code" is genuinely yours to decide.

## Purpose

A page that compares NHS trusts against each other on a chosen waiting-times
measure, scoped either to all of England or to a single NHS region. It sits
alongside the existing per-org page. The unit of comparison is always the trust;
region is a filter on "compared against whom," not a separate unit.

## Scope decisions already made

- **Comparator scope = England or NHS region only.** ICB is deliberately NOT a
  comparator scope in v1. Reason: a trust↔region mapping is clean and one-to-one,
  whereas trust↔ICB is many-to-many (ICBs are commissioners) and needs an
  attribution convention we haven't settled. ICB is a documented later addition
  (see "Deferred").
- **Two views of the scoped group, both distribution-based:**
  1. **Funnel plot** (primary): performance on y, denominator volume on x, with
     control limits. Shows ALL in-scope trusts, including low-volume ones.
  2. **Percentile view** (companion): where each trust sits in the spread.
     EXCLUDES trusts below the denominator threshold.
- **Measure = full breakdown.** User picks a standard (FDS28 / CMB31 / CMB62),
  then optionally narrows by the breakdown dimensions already in the tidy store
  (cancer / route / modality). All-cancers headline is the default.
- **Rest of England shown as a reference band/line** behind the scoped group when
  a region is selected, so the national anchor is never lost.

## Methods rules (must hold; these are the credibility of the tool)

1. **Control limits are anchored to the NATIONAL distribution**, not recomputed
   within the scoped region. "Outlier" always means "outlier relative to England."
   Recomputing limits inside a small group gives unstable, misleading limits.
   Use 95% and 99.8% limits (2 and 3 SD equivalents), matching standard funnel
   methodology and the study protocol.
2. **Denominator threshold:** a trust-month (or trust-period aggregate) below the
   reliability threshold is sub-threshold. Reuse the existing pipeline threshold
   (denominator ≥ 10) — do not invent a second one. Open for Code: whether the
   comparison aggregates to a single recent period or a trailing window; recommend
   the most recent FINAL period by default with the period stated on screen.
3. **Sub-threshold trusts appear in the funnel only.** The funnel is volume-aware
   by construction (low volume → wide limits), so showing them is honest. The
   percentile view excludes them because a tiny denominator yields a wild,
   falsely-authoritative percentile. The SAME trust may legitimately appear in the
   funnel and not the percentile view — this is intended; add a one-line on-screen
   note explaining it.
4. **Automatic scope fallback.** The fallback is triggered by the MEASURE+SCOPE
   combination, evaluated AFTER both are chosen, on the count of trusts clearing
   the threshold for that specific measure:
   - If a region has fewer than **5** threshold-clearing trusts for the chosen
     measure, widen one step to England and announce it.
   - One-step widen only (region → England). Never dead-end on an error.
   - The user's original region selection stays visible in the control, with a
     clear notice: e.g. "Too few trusts in {Region} meet the reliability threshold
     for {measure} to compare meaningfully. Showing England instead."
   - The fallback is dynamic: switching to a granular breakdown can trigger it even
     though the scope selector hasn't changed.
   (Note: with regions-only, fallback will rarely fire — whole regions almost
   always clear 5 trusts — but the rule must exist for granular breakdowns.)
5. **October 2023 comparability break** applies here as everywhere: 31-day and
   62-day are not comparable across Oct 2023. The comparison defaults to data from
   2023-10 onward; surface the existing meta note.

## Data / pipeline work (Code's territory)

- Attach **NHS region** to every provider trust. Confirm whether region is
  derivable from the CWT file's Parent_Org / existing fields, or needs the ODS
  organisation reference lookup. If a lookup is required, add it as a pipeline
  stage joined on ODS code, and document it. Flag back if region turns out to be
  as messy as ICB — the whole regions-only rationale rests on it being clean.
- The tidy store ALREADY contains the breakdown rows (cancer/route/modality) —
  keep them. The comparison view consumes them; do not narrow the store.
- Build whatever per-measure aggregated artefact the comparison page needs (open
  for Code: precompute comparison JSON at build time vs compute client-side from
  the tidy data). Given the breakdown combinatorics, precomputing the common
  measures at build time is likely cleaner, but that's your call.

- **Download strategy (replaces the single 200 MB cwt_tidy.csv as the primary
  download).** A 200 MB single file is hostile to the research/analyst audience.
  Instead produce targeted slices plus a compressed full file:
  - Per-financial-year files (one CSV per FY).
  - A small **all-cancers headline** extract (the "all" slice only) — a fraction
    of the rows, covers most users' needs.
  - The full tidy file available **gzipped** for the minority who want everything
    (a 200 MB CSV should gzip to roughly 30–40 MB).
  - Open for Code: exact file naming and whether to also split by standard. The
    front-end download UI (what's offered, how it's labelled) is a planning-session
    decision — provide the files; we'll design the UI.

- **Suppress non-real placeholder orgs from selection, keep them in the store.**
  The store contains an UNKNOWN ICB (~6,680 rows) — a legitimate "unallocated
  commissioner" bucket, not a real organisation. Exclude UNKNOWN (and any similar
  placeholder) from index.json (the picker) and from the comparison view, because
  no user would meaningfully compare against it. But RETAIN it in the tidy store
  and in the national totals — dropping it would make sums fail to reconcile.
  Same keep-in-store / hide-from-selection pattern as the breakdown rows. With
  regions-only scoping this mostly takes care of itself (ICBs aren't a comparator
  scope), but it must also be excluded from the per-org picker.

## Front end (will be refined in planning session)

- Controls: measure selector (standard → optional cancer/route/modality) and
  scope selector (England / region).
- Funnel plot primary, percentile view as companion, England reference band.
- Visible methods notes: national-anchored limits, the threshold + why low-volume
  trusts are funnel-only, any active fallback, the Oct-2023 break.
- Match the existing dashboard's visual language (the clinical chart-paper style
  in site/index.html). Detailed visual design comes from the planning session;
  don't over-invest in styling before that.

## Deferred (record in DECISIONS.md, do not build yet)

- **ICB as a comparator scope.** Requires a documented trust→ICB attribution
  convention. When added, reuse whatever convention the main study protocol
  settles on, so dashboard and research stay methodologically aligned. ICB data
  stays in the tidy store meanwhile; per-trust pages may still show a trust's ICB
  as a label.
- Ranked league-table view (deliberately not the centrepiece, to resist
  league-table misreading; can be added later if users ask).
- Trailing-window smoothing of the comparison metric, if the single-period view
  proves too noisy.

## Sequencing question for the user (answer before Code starts)

Build the whole view in one pass, or stage it: (a) funnel + region scoping on the
all-cancers headline first, then (b) breakdown selector + fallback logic second?
Planning session recommends a single spec so Code doesn't architect v1 in a way
that needs unpicking, but staging gets something on screen sooner.
