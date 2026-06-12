# Spec: v7 — labelling, copy, composition, Oct-2023 marker + org-hiding investigation

Source: planning session. Per-org page. Mix of front-end and pipeline. Most is
settled and buildable now; the org-hiding threshold is investigate-first.

## Part 1 — Front-end / labelling (all settled, build now)

1. Title -> "NHS Cancer Waiting Times Dashboard".
2. Subtitle -> "England · Performance against NHS Cancer Waiting Time Targets".
3. Provider dropdown: group into "NHS Trust" and "Other", NHS Trusts first.
   (Use org name / type to classify; flag back if the data doesn't cleanly
   distinguish an NHS trust from a non-trust provider.)
4. Selected-provider byline: remove the "Provider (trust)" prefix. E.g.
   "AIREDALE NHS FOUNDATION TRUST · North East and Yorkshire".
5. Commissioner dropdown: group into "ICB" and "Other", ICBs first.
6. Selected-commissioner byline: remove the "Commissioner (ICB)" prefix.
7. Remove the helper text "NHS England's ten tumour-site groups · applies to all
   three cards and the chart." next to the Cancer Group dropdown.
8. Move the Oct-2023 comparability banner from above to BELOW the chart.

## Part 2 — Data items (settled, build now)

9. **Exclude Missing/Invalid from "Other".** The "Other" cancer group must no
   longer include Missing/Invalid (it's data-quality residue, not a clinical
   category). CONSEQUENCE (confirmed acceptable): the ten groups will no longer
   sum exactly to the all-cancers headline — the difference is the Missing/Invalid
   count. Update/relax the reconciliation guard accordingly so this intentional
   gap doesn't trip it; keep the guard's protection against the corrupting
   direction (groups exceeding the total = double-count). Document the change.

10. **Cancer-group composition description.** When a COMPOSITE group is selected,
    show a short description of which raw types it aggregates. Composite groups
    only (Haematology, Upper GI, Urology, Other) — NOT the six 1:1 groups, which
    are self-explanatory. Example: Other -> "brain/CNS, sarcoma, children's
    cancer, non-specific symptoms". Source the membership from the existing
    cancer_groups.py lookup so the description can't drift from the actual
    mapping. (Note: after item 9, Other's description should NOT list
    Missing/Invalid.)

11. **Oct-2023 change marker on charts.** Add a vertical dashed line at Oct 2023
    on the CMB31 and CMB62 charts, labelled (e.g. "standards changed"). NOT on
    FDS28 (no break). This complements the banner (now below the chart).

## Part 3 — Org hiding (INVESTIGATE FIRST, don't build the cut yet)

The user wants orgs with negligible data hidden from the pickers (e.g. CSH Surrey
shows n=1 / n=0 low-reliability across the board — clutter that produces empty
charts). The principle is agreed; the threshold is not. Please REPORT before
cutting:
- The distribution of org activity: for providers and commissioners separately,
  how many orgs would be hidden under candidate rules, e.g.:
  (a) fails reliability (n<10) in all months across all standards;
  (b) all-cancers denominator below X in the latest period / on average;
  (c) no single standard reaching meaningful volume.
- A sense of where the natural cut is (is there a clean gap between real orgs and
  noise orgs, like there was for routes?).
- Confirm hiding is for SELECTION only (picker + default lists); the data stays
  in the store and the org remains reachable by direct link if it exists.
Report this and the user will pick the rule. Then a follow-up applies it.

## After building

- Re-render: the relabelled header/bylines; a composite group showing its
  composition description; a CMB62 chart showing the Oct-2023 marker; the grouped
  provider and commissioner dropdowns.
- Report the org-hiding distribution (Part 3).
- Log in DECISIONS.md. Pause before deploy.
