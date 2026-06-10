# Spec: Per-organisation page visual refinements (v4)

Source: planning session. Front-end changes to the per-org page (site/index.html).
No pipeline change expected; flag back if any data field is missing.

## 1. Three type buttons above the org dropdown

- Add three buttons at the top of the org selector: **National | Providers | Commissioners**.
- Below them, a dropdown of the specific organisations for the chosen type:
  - National selected -> NO dropdown (it's just England); hide or disable it.
  - Providers selected -> dropdown of the 201 trusts.
  - Commissioners selected -> dropdown of the 50 ICBs.
- On switching type to Providers or Commissioners, default to the FIRST org
  alphabetically so the chart is never blank.
- Default page load stays National (unchanged).
- The active type button is visually marked as selected.

## 2. Searchable dropdowns

- Make the dropdowns type-to-filter (search as you type), not scroll-only.
- Applies to BOTH the organisation dropdown and the breakdown dropdown.
- Keep keyboard and click selection working.

## 3. Size-of-the-prize follows the selected standard

- Remove the standard selector dropdown inside the Size-of-the-prize panel.
- The panel now always reflects the standard currently active (the one selected
  via the summary cards / shown in the big chart). Switching standard updates the
  card, the chart, AND this panel together.
- Keep the target slider in the panel.

## 4. Legend: show the dot as well as the line

- Each legend entry should display its MARKER (dot) style alongside its line
  style, so "this organisation", "England", "provisional", and "low reliability"
  are each visually unambiguous, matching exactly how they render on the chart.

## 5. Recolour low-reliability markers to muted org colour

- Currently low-reliability (n<10) markers/segments are grey, too close to the
  faint England comparison line -> confusing.
- Change them to a MUTED / LIGHTER version of the organisation's own colour
  (lighter/desaturated teal), NOT full-strength.
- Rationale: they must clearly belong to the org's series (distinct from the grey
  England line), while STILL reading as de-emphasised/fragile (not as confident as
  the solid reliable line). Do not make them as bold as the reliable org line.
- Keep the dashed/de-emphasised line segments from v3; just change their colour
  family from grey to muted-org. Update the legend swatch (item 4) to match.

## After building

Re-render for review: (a) National default, (b) a Provider selected via the new
buttons, (c) the searchable dropdown open mid-search, (d) a thin slice showing the
new muted-teal low-reliability treatment next to the England line (to confirm they
are now distinguishable). Log in DECISIONS.md. Pause before deploy.
