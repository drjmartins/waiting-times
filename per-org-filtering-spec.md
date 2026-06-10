# Spec: Per-organisation breakdown filtering (v3)

Source: planning session. Follow-on to the v2 redesign. Build after v2 is
deployed. Touches the pipeline (a new per-org breakdown file) + the front end.

## What the data allows (from Code's investigation — read first)

NHS publishes single dimensions and SELECTED PAIRWISE combinations only. There
are ZERO three-way (cancer x route x modality) cells. So:
- No arbitrary Cartesian cross. Offer single-dimension filters + the specific
  pairwise combos that actually exist in the data.
- Available dimensions differ by standard:
  - FDS28: cancer type only (no route, no modality).
  - CMB31 / CMB62: cancer, route/stage, modality, + the published pairwise combos.
- The UI must RESHAPE per standard, not grey-out unavailable options.

## Goal

On the per-org page, let the user narrow the chart from "all cancers" to a
specific breakdown slice (e.g. lung; or screening route; or surgery modality; or
a published pair like lung + urgent-suspected-cancer), for the selected standard
and organisation.

## Pipeline change (load-on-demand)

- Keep the lean `org/<CODE>.json` (all-slice only) for fast first paint.
- Emit a NEW `org/<CODE>.breakdown.json` per org, containing the breakdown series
  (cancer / route / modality + the existing pairwise combination rows) for all
  standards. ~20-40 KB gz per org per Code's measurement — fine on demand.
- Fetch the breakdown file ONLY when the user first opens a filter, not on page
  load.
- Same series shape as the all-slice (months, performance, within_target, total,
  data_status) so the chart renders breakdown slices with no new chart code.

## Front-end behaviour

- A filter control appears near the chart, defaulting to "All cancers".
- Options are driven by what exists for the current standard + org (built from
  the breakdown file once loaded). Single dimensions first; published pairwise
  combos surfaced as their own labelled options where they exist (do NOT present
  two free dropdowns that imply non-existent crosses).
- Selecting a slice redraws the big chart for that slice.
- National comparison line MATCHES the selected slice (national lung vs the org's
  lung — like-for-like). If the matching national slice is unavailable, hide the
  comparison line rather than fall back to all-cancers.
- Sub-threshold months (denominator < 10) are SHOWN but visually FLAGGED as
  low-reliability (e.g. open markers + a note), not hidden — narrow slices at one
  org will often be thin.
- Switching standard or org resets/reshapes the filter to that context's valid
  options (keep "All cancers" as the safe default).
- Tooltip unchanged (month, %, within/total, provisional/final).

## Interaction with v2

- The three summary cards stay all-cancers (they're the headline overview).
  Filtering applies to the big chart only.
- Size-of-the-prize: out of scope for v1 of filtering — leave it on all-cancers.
  (Revisit later if wanted.)

## Edge cases to handle

- Empty/absent slice for an org: show "No data published for this breakdown at
  this organisation" rather than a blank chart.
- FDS28 with route/modality: those options must not appear at all.
- Provisional tail behaves as in v2 (dashed/hollow).

## After building

Re-render for review: (a) a provider on a single-dimension slice (e.g. lung,
CMB62) showing the matched national line, (b) FDS28 showing cancer-only options,
(c) a thin slice showing the low-reliability flagging. Log in DECISIONS.md.
Pause before deploy.
