# Spec: Per-organisation page redesign (v2)

Source: planning session. Hand to Claude Code. This is front-end work on the
existing per-org page (site/index.html). NO pipeline change is required — all
data needed (per-org JSON, national.json, within-target + total counts,
provisional/final flags) already exists in the build. If that turns out not to be
true for any field, flag back before building rather than changing the pipeline.

## Goal

Turn the per-org page from a three-small-charts overview into a focused
single-chart explorer with national context as the default anchor, all three
standards visible at a glance as summary cards, and full data on hover.

## Changes

### 1. Default to National

- The page loads showing National (the single England line from national.json),
  NOT the first organisation alphabetically.
- National is the all-England anchor. It should be reachable in one click at any
  time (see picker below).

### 2. Organisation picker grouped Providers vs Commissioners

- Replace the flat alphabetical picker with a grouped one:
  - **National** pinned at the top (it is the anchor, neither a provider nor a
    commissioner in browsing terms).
  - **Providers (trusts)** — the 201 provider orgs.
  - **Commissioners (ICBs)** — the 50 ICB orgs.
- Each group alphabetical within itself. org_level is already in index.json, so
  grouping is a front-end concern.
- (UNKNOWN remains suppressed, as already implemented.)

### 3. Single large chart + three summary cards as switcher

- Replace the three small per-standard charts with ONE large time-series chart.
- Above it, three **summary cards**, one per standard (FDS28, 31-day, 62-day):
  - Each shows the standard's name, the latest performance figure, and a small
    sparkline of the recent trend.
  - The cards are the switcher: clicking a card loads that standard into the big
    chart below. The active card is visually marked as selected.
- The big chart shows, for the selected standard: the full monthly time series
  for the current org, the national comparison line (faint), the target marker,
  and provisional months styled distinctly from finalised (e.g. lighter/dashed).
- Keep the existing chart-paper visual language.

### 4. Hover tooltips on the big chart

- Hovering a data point shows a tooltip with: month (e.g. "Sep 2025"),
  performance %, within-target count, total (denominator), and the
  provisional/final flag. Example: "Sep 2025 — 71.9% — 8,432 of 11,710 — final".

## Interaction details (specify so they aren't guessed)

- Switching ORGANISATION updates the three cards AND the big chart together to the
  new org, and KEEPS the currently-selected standard (don't reset to FDS each
  time) — so the user can flip between orgs while staying on, say, 62-day.
- Switching STANDARD (clicking a card) changes only the big chart; the org stays.
- On first load (National, default), pick a sensible default standard for the big
  chart — 62-day combined is the most-watched, suggest defaulting to it, but
  Code's call.

## Out of scope (later, don't build now)

- The "compare this trust" link from here into the comparison page (separate,
  planned task).
- Any change to the comparison page (compare.html).
- Download UI.

## After building

Re-render the per-org page on (a) National default load and (b) one provider with
a non-default standard selected, so the planning session can review the layout,
the cards-as-switcher behaviour, and a tooltip. Log in DECISIONS.md. Pause before
deploy as usual.
