# Spec: Context-aware breakdown dropdowns (v6)

Source: planning session, after Code's hierarchy investigation. Per-org page.
Builds on the v5 cancer-group selector. Item 1 (remove Size of the Prize) is
separate and deploys first.

## What the data supports (from Code's investigation — the hard constraint)

- **cancer group -> route**: real. Selecting a group can narrow the route
  dropdown. NEEDS a pipeline change: composite groups (Haematology, Upper GI,
  Urology, Other) require their raw cancer x route combos aggregated (sum
  numerator + denominator across members — the same rollup pattern as the
  existing cancer_group dim). Precompute a cancer_group x route dim at build time.
- **route -> modality**: real, but ONLY as an all-cancers slice. Exists for
  CMB31/CMB62, already in the breakdown files.
- **cancer group -> route -> modality (three-way)**: DOES NOT EXIST. NHS does not
  publish it. The modality level can never be nested under a chosen cancer group.
- **FDS28**: no route/modality dims (its 2nd dim is referral stage); no modality
  level at all.

## The design (confirmed with the user)

A **group-aware route dropdown** for all standards where routes exist, PLUS a
**second modality dropdown that appears ONLY in the all-cancers view** and
disappears when a specific cancer group is selected.

### Level 1 — route dropdown (group-aware)

- The existing breakdown dropdown becomes context-aware on the selected cancer
  group: it lists only the routes published for that group + standard.
- All-cancers selected: routes shown as today (all published routes).
- A specific group selected (e.g. Breast): the route dropdown shows only that
  group's routes (e.g. CMB62: Breast Symptomatic, Consultant Upgrade, Screening,
  Urgent Suspected Cancer). CMB31: First Treatment, Subsequent. FDS28: its
  referral-stage options.
- Selecting a route redraws the big chart for group x route.

### Level 2 — modality dropdown (ALL-CANCERS ONLY)

- A SECOND dropdown for modality (Anti-cancer drug regimen, Other, Radiotherapy,
  Surgery) appears ONLY when:
  - the cancer group is "All cancers", AND
  - the standard is CMB31 or CMB62 (never FDS28), AND
  - a route is selected that has a published modality level.
- It selects an all-cancers route x modality slice for the big chart.
- The moment a specific cancer group is selected, this modality dropdown HIDES.

### State transitions (specify exactly — don't leave to guesswork)

- Selecting a specific group while a modality is chosen: the modality dropdown
  hides AND its selection RESETS. The chart falls back to the group's route-level
  view. (Do not preserve hidden modality state.)
- Returning to All cancers: the modality dropdown reappears at its DEFAULT
  ("all"/none), not at any previously chosen value.
- Switching standard to FDS28: modality dropdown not shown at all.
- Keep all dropdowns searchable (v4 behaviour).
- Low-reliability (n<10) treatment applies to these narrower slices as before.

## Item 1 (separate, deploy first)

Remove Size of the Prize — already built and rendered; deploy standalone now per
user confirmation.

## Pipeline change required

Precompute the cancer_group x route combination dim (aggregating composite groups
by summing num/denom). Add a reconciliation check: a group's routes should sum to
that group's all-routes total. route x modality already exists, no change.

## After building

Re-render for review:
(a) a group selected (e.g. Breast, CMB62) showing only its routes, no modality dropdown;
(b) all-cancers + CMB62 + a route with the modality 2nd dropdown visible;
(c) the transition — show that picking a group hides/resets the modality dropdown;
(d) FDS28 showing no modality dropdown.
Log in DECISIONS.md. Pause before deploy.
