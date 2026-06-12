"""
Aggregate raw CWT Cancer_Type labels into NHS England's ten standard tumour-site
groups (the groups used by NHS England's own CWT dashboard:
https://data.england.nhs.uk/dashboard/cancer-wait-times).

    Breast, Gynaecology, Haematology, Head & Neck, Lower GI, Lung, Other, Skin,
    Upper GI, Urology.

WHY THIS MAPPING IS NOT IMPROVISED
----------------------------------
The ten group names are NHS England's own. The backbone of the mapping is taken
DIRECTLY from the source labels NHS England publishes in the Combined (ICB-based)
CWT file, which already encode the hierarchy:
  * The CMB31 / CMB62 top-level labels ARE the group names verbatim
    ('Breast', 'Gynaecological', 'Haematological', 'Head & Neck',
     'Lower Gastrointestinal', 'Lung', 'Other (a)', 'Skin',
     'Upper Gastrointestinal', 'Urological').
  * Sub-breakdowns are parent-prefixed, so NHS's own naming declares the parent
    group: 'Haematological - Lymphoma' -> Haematology, 'Urological - Prostate'
    -> Urology, 'Upper Gastrointestinal - Hepatobiliary' -> Upper GI, etc.
  * CMB62 splits two "rare cancers" out at the top level —
    'Acute leukaemia' (a haematological malignancy) and 'Testicular' — alongside
    'Haematological (Excluding Acute Leukaemia)' and
    'Urological (Excluding Testicular)'. The CWT dataset guidance (National CWT
    Monitoring Dataset Guidance v10.0, §5.5 / §6) names acute leukaemia,
    testicular and children's cancers as the three "rare cancers" and lists
    acute leukaemia among haematological malignancies — so they roll back into
    Haematology / Urology, restoring the ten groups.

The FDS28 "Suspected ..." labels name the clinical site and map to the same ten
groups. FOUR FDS28-only labels have NO dedicated group among NHS's ten
(brain/CNS, sarcoma, children's cancer, non-specific symptoms); NHS's CMB
reporting — which uses exactly these ten groups — carries no brain/sarcoma/
children's/NSS line, so those cohorts sit inside CMB "Other". We therefore map
them to Other (the spec's designated catch-all). These by-elimination
assignments are flagged in DECISIONS.md and the Part A report — they are the
only places we infer rather than read a group straight off NHS's label.

'Missing or Invalid' (a data-quality bucket, FDS28 only) is DELIBERATELY EXCLUDED
from the ten groups (v7): it is not a clinical category, so it maps to the
sentinel EXCLUDED_GROUP rather than to Other. It stays in GROUP_OF so group_for
remains exhaustive (a genuinely-new label still fails loudly), but the rollup
iterates TEN_GROUPS and so drops it. INTENDED CONSEQUENCE: the ten groups no
longer sum EXACTLY to the all-cancers headline — the shortfall is precisely the
Missing/Invalid count (FDS28 only; ~0.28% of FDS activity, zero in CMB31/CMB62).
The reconciliation test is relaxed for that one-directional gap but still guards
the corrupting direction (groups must never EXCEED the total).

DOUBLE-COUNTING SAFETY
----------------------
Within CMB, a parent label (e.g. 'Haematological') and its children
('Haematological - Lymphoma' + '- Other (a)') both map to the same group. In the
real data they NEVER co-occur in the same (month, org, standard) — the source
uses one granularity per vintage — so summing every present member of a group is
correct. `assert_no_double_count` is a guard that fails loudly if a future NHS
vintage ever ships a parent AND its children together (which would double the
denominator), so we catch it rather than silently inflating a group.
"""

# Canonical ten groups, in the order NHS England's dashboard lists them.
TEN_GROUPS = (
    "Breast",
    "Gynaecology",
    "Haematology",
    "Head & Neck",
    "Lower GI",
    "Lung",
    "Other",
    "Skin",
    "Upper GI",
    "Urology",
)

# Sentinel "group" for labels that are intentionally NOT part of the ten
# tumour-site groups (currently only 'Missing or Invalid', a data-quality
# bucket). Distinct from any real group so the rollup — which iterates
# TEN_GROUPS — silently drops it; group_for still returns a value, so the
# exhaustiveness guard keeps catching genuinely-new NHS labels.
EXCLUDED_GROUP = "(excluded — data quality)"

# The COMPOSITE groups: built from more than one distinct clinical sub-site, so
# a short "what's in here" description helps. The six 1:1 groups (Breast,
# Gynaecology, Head & Neck, Lower GI, Lung, Skin) are self-explanatory and have
# no entry (see composition_text).
COMPOSITE_GROUPS = ("Haematology", "Upper GI", "Urology", "Other")

# Human-readable make-up of each composite group. Each item pairs a DISPLAY
# sub-site with the raw GROUP_OF label(s) that evidence it, so the description is
# SOURCED FROM the mapping rather than free-floating copy: the build calls
# assert_composition_consistent(), which fails loudly if any cited label stops
# mapping to that group (drift guard). 'Other' intentionally lists only the four
# extra clinical sites it absorbs — not its own 'Other (a)' catch-all label, and
# (post-v7) not 'Missing or Invalid', which is now excluded from the group.
_COMPOSITION = {
    "Haematology": [
        ("lymphoma", ("Haematological - Lymphoma",)),
        ("acute leukaemia", ("Acute leukaemia",)),
        ("other haematological malignancies", ("Haematological - Other (a)",)),
    ],
    "Upper GI": [
        ("oesophagus & stomach", ("Upper Gastrointestinal - Oesophagus & Stomach",)),
        ("hepatobiliary", ("Upper Gastrointestinal - Hepatobiliary",)),
    ],
    "Urology": [
        ("prostate", ("Urological - Prostate",)),
        ("testicular", ("Testicular",)),
        ("other urological", ("Urological - Other (a)",)),
    ],
    "Other": [
        ("brain/CNS", ("Suspected brain/central nervous system tumours",)),
        ("sarcoma", ("Suspected sarcoma",)),
        ("children's cancer", ("Suspected children's cancer",)),
        ("non-specific symptoms", ("Suspected cancer - non-specific symptoms",)),
    ],
}


def composition_text(group):
    """Human-readable constituent list for a COMPOSITE group, e.g. Haematology ->
    'lymphoma, acute leukaemia, other haematological malignancies'. Returns "" for
    the six self-explanatory 1:1 groups (no description shown)."""
    items = _COMPOSITION.get(group)
    return ", ".join(name for name, _labels in items) if items else ""


def assert_composition_consistent():
    """Drift guard (run at build time): every raw label cited in a composite
    group's description must still map to that group in GROUP_OF, and every
    composite group must be one of the ten. A mapping change that orphans a
    description then fails the build rather than shipping a stale composition."""
    for grp, items in _COMPOSITION.items():
        if grp not in TEN_GROUPS:
            raise ValueError(f"composition group {grp!r} is not one of the ten groups")
        for name, labels in items:
            for lab in labels:
                if GROUP_OF.get(lab) != grp:
                    raise ValueError(
                        f"composition for {grp!r} cites {lab!r}, which maps to "
                        f"{GROUP_OF.get(lab)!r} in GROUP_OF — the description has drifted "
                        f"from the mapping; update cancer_groups._COMPOSITION.")

# Parent -> set of child labels, for the double-counting guard. Only CMB labels
# form hierarchies; both parent and children map to the same group below.
_PARENT_CHILDREN = {
    "Haematological": {
        "Haematological - Lymphoma",
        "Haematological - Other (a)",
    },
    "Upper Gastrointestinal": {
        "Upper Gastrointestinal - Hepatobiliary",
        "Upper Gastrointestinal - Oesophagus & Stomach",
    },
    "Urological": {
        "Urological - Other (a)",
        "Urological - Prostate",
    },
    # CMB62 top-level "Excluding ..." parents whose excluded part is a sibling
    # rather than a child, but which still must not co-occur with the finer split.
    "Haematological (Excluding Acute Leukaemia)": {
        "Haematological - Lymphoma",
        "Haematological - Other (a)",
    },
    "Urological (Excluding Testicular)": {
        "Urological - Other (a)",
        "Urological - Prostate",
    },
}

# Explicit raw-label -> group lookup. EXHAUSTIVE over every Cancer_Type value
# NHS England currently publishes across FDS28 / CMB31 / CMB62. group_for()
# raises on anything not listed, so a new NHS label fails the guard/test rather
# than silently vanishing.
GROUP_OF = {
    # ---- Breast ----
    "Breast": "Breast",
    "Suspected breast cancer": "Breast",
    "Exhibited (non-cancer) breast symptoms - cancer not initially suspected": "Breast",
    # ---- Gynaecology ----
    "Gynaecological": "Gynaecology",
    "Suspected gynaecological cancer": "Gynaecology",
    # ---- Haematology ----
    "Haematological": "Haematology",
    "Haematological - Lymphoma": "Haematology",
    "Haematological - Other (a)": "Haematology",
    "Haematological (Excluding Acute Leukaemia)": "Haematology",
    "Acute leukaemia": "Haematology",
    "Suspected acute leukaemia": "Haematology",
    "Suspected haematological malignancies (excluding acute leukaemia)": "Haematology",
    # ---- Head & Neck ----
    "Head & Neck": "Head & Neck",
    "Suspected head & neck cancer": "Head & Neck",
    # ---- Lower GI ----
    "Lower Gastrointestinal": "Lower GI",
    "Suspected lower gastrointestinal cancer": "Lower GI",
    # ---- Lung ----
    "Lung": "Lung",
    "Suspected lung cancer": "Lung",
    # ---- Skin ----
    "Skin": "Skin",
    "Suspected skin cancer": "Skin",
    # ---- Upper GI ----
    "Upper Gastrointestinal": "Upper GI",
    "Upper Gastrointestinal - Hepatobiliary": "Upper GI",
    "Upper Gastrointestinal - Oesophagus & Stomach": "Upper GI",
    "Suspected upper gastrointestinal cancer": "Upper GI",
    # ---- Urology ----
    "Urological": "Urology",
    "Urological - Other (a)": "Urology",
    "Urological - Prostate": "Urology",
    "Urological (Excluding Testicular)": "Urology",
    "Testicular": "Urology",
    "Suspected testicular cancer": "Urology",
    "Suspected urological malignancies (excluding testicular)": "Urology",
    # ---- Other (NHS catch-all; FDS28-only sites with no dashboard group + DQ) ----
    "Other (a)": "Other",
    "Suspected other cancer": "Other",
    "Suspected brain/central nervous system tumours": "Other",
    "Suspected sarcoma": "Other",
    "Suspected children's cancer": "Other",
    "Suspected cancer - non-specific symptoms": "Other",
    # Data-quality residue (FDS28 only) — intentionally NOT one of the ten groups
    # (v7). Mapped to the sentinel so group_for stays exhaustive but the rollup
    # drops it; see module docstring + EXCLUDED_GROUP.
    "Missing or Invalid": EXCLUDED_GROUP,
}


class UnmappedCancerType(KeyError):
    """Raised when a raw Cancer_Type value has no group. Fail loudly so a new
    NHS label can't silently disappear from the aggregated totals."""


def group_for(label):
    """Map one raw Cancer_Type label to its NHS group. Raises UnmappedCancerType
    if the label is unknown (the exhaustiveness guard)."""
    key = str(label).strip()
    try:
        return GROUP_OF[key]
    except KeyError:
        raise UnmappedCancerType(
            f"Unmapped Cancer_Type {label!r}. Add it to GROUP_OF in "
            f"pipeline/cancer_groups.py (catch-all group is 'Other')."
        )


def assert_all_mapped(labels):
    """Guard: every label in `labels` must map. Returns the sorted set of
    distinct labels checked. Raises UnmappedCancerType listing ALL misses."""
    missing = sorted({str(l).strip() for l in labels} - set(GROUP_OF))
    if missing:
        raise UnmappedCancerType(
            f"{len(missing)} unmapped Cancer_Type value(s): {missing}. "
            f"Add each to GROUP_OF in pipeline/cancer_groups.py."
        )
    return sorted({str(l).strip() for l in labels})


def assert_no_double_count(labels_present):
    """Guard against parent+child co-occurrence within a single
    (month, org, standard) cell, which would double a group's denominator.
    `labels_present` = the raw labels present in that cell. Raises ValueError if
    a parent and any of its children both appear."""
    present = {str(l).strip() for l in labels_present}
    for parent, children in _PARENT_CHILDREN.items():
        if parent in present and (present & children):
            raise ValueError(
                f"Double-count risk: parent {parent!r} and child(ren) "
                f"{sorted(present & children)} both present in one cell. NHS "
                f"changed granularity within a vintage — review cancer_groups.py."
            )
