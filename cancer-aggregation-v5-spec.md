# Spec: Cancer-type aggregation + shared breakdown filter (v5)

Source: planning session. Two linked pieces: (A) a PIPELINE change to aggregate
raw cancer types into NHS England's ten standard groups, and (B) a FRONT-END
change to use those groups as a shared breakdown filter above the three summary
cards. Build A first; B depends on A validating cleanly.

## Why

The user wants a breakdown filter that drives all three standard cards at once.
We parked this before because raw cancer-type labels differ by standard. Solving
it via aggregation: roll raw labels into a small set of groups that exist across
ALL three standards, so one selector applies consistently.

## Part A — Pipeline: aggregate cancer types into NHS groups

### The target groups (match NHS England's own dashboard)

Ten site-based groups, exactly as NHS England's CWT dashboard uses:
Breast, Gynaecology, Haematology, Head & Neck, Lower GI, Lung, Other, Skin,
Upper GI, Urology.

Source to match: https://data.england.nhs.uk/dashboard/cancer-wait-times

### Tasks

1. **Source the official mapping.** Find NHS England's published definition of
   which granular Cancer_Type values roll into each of the ten groups. Use THAT
   mapping, do not improvise. If the published mapping can't be found, FLAG BACK
   rather than guessing an approximate one (an improvised mapping defeats the
   point of matching the canonical source).
2. **Build an explicit lookup** from every raw Cancer_Type value -> one of the
   ten groups. The mapping must be EXHAUSTIVE: every raw value lands in exactly
   one group ("Other" is the catch-all). Add a guard/test that fails if any raw
   value is unmapped, so a future new NHS label can't silently vanish.
3. **Aggregate by summing, not averaging.** For each (month, org, standard,
   group), sum the numerators and sum the denominators across the constituent
   cancer types, then compute performance from the totals. Do NOT average the
   per-type percentages.
4. **Validate across all three standards (the gate for Part B).** Confirm each
   of the ten groups can be constructed from labels present in FDS28, CMB31, AND
   CMB62. FDS28's cancer-type labels differ (e.g. "suspected"/"exhibited
   symptoms" categories), so a per-standard label->group view may be needed that
   still rolls up to the same ten group names. REPORT which groups reconcile in
   all three standards and which (if any) do not. If a group is missing from a
   standard, do not silently leave it out, flag it so we decide how the shared
   filter handles it.
5. **Keep the existing granular breakdowns too.** Add the ten groups ALONGSIDE
   the existing raw cancer/route/modality data in the breakdown file, not as a
   replacement. The big chart can still offer granular slices; the new groups are
   an additional, coarser layer. (Confirm payload stays reasonable.)

### Output

The per-org breakdown file gains the ten aggregated cancer groups per standard.
Keep the all-cancers "all" slice as-is for the headline.

## Part B — Front end: shared cancer-group filter above the cards

ONLY build once Part A's validation (task 4) confirms the groups work across all
three standards. If some group fails to reconcile, pause and report before building B.

1. Add a shared **cancer group** selector ABOVE the three summary cards
   (Breast / Gynaecology / ... / Urology, plus "All cancers" as default).
2. Selecting a group updates ALL THREE cards AND the big chart to that group's
   aggregated series for the current org. Switching standard (cards) keeps the
   selected group; switching org keeps the selected group; default is All cancers.
3. The cards' sparklines now show the selected group's series. NOTE: group-level
   series at one org can still be thin in some months, apply the same
   low-reliability treatment (muted-teal/dashed, n<10) already used on the big
   chart, and keep it legible at sparkline size (or at minimum don't let a thin
   group read as a confident sparkline).
4. The big chart's EXISTING breakdown selector (granular cancer/route/modality)
   stays for deeper drilling. Decide on review whether the shared group filter
   and the big-chart granular filter coexist or the big chart inherits the shared
   group as its default, bring this to the planning session if it gets fiddly
   rather than guessing.
5. Searchable dropdown behaviour as per v4.

## After building

- Part A: report the mapping source, the cross-standard validation result, and a
  reconciliation check (do the ten groups' summed denominators equal the
  all-cancers denominator per org-month-standard? they should, modulo any
  unmapped-value handling).
- Part B: re-render for review (All cancers default; a group e.g. Lung selected
  showing all three cards + big chart updated; a thin group showing the
  low-reliability treatment on a sparkline).
- Log in DECISIONS.md. Pause before deploy.
