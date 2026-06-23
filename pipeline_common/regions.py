"""Shared provider-code -> NHS region lookup.

The RTT "Full CSV" source carries no provider region (only a Commissioner Parent
/ ICB), so the RTT build historically wrote region "England" for every org. The
cancer CWT source DOES carry it (Parent_Org, verified one-to-one with the 7 NHS
England regions). Rather than introduce a second region source for RTT, this
reuses the region the cancer dashboard already derived: it reads the committed
cancer index.json and exposes {code: region} for codes with a real (non-England)
region.

So an RTT provider's region is, by construction, identical to the same trust's
region on the cancer dashboard ("same field"). Codes absent from the cancer
index (e.g. RTT-only independent-sector providers) get no region, exactly like a
region-less cancer provider — the caller defaults them to "England" and the
front end shows nothing.

Fail-open: a missing or unreadable cancer index returns {} so a region-source
hiccup never breaks the RTT build; regions simply don't show that run.
"""
import json


def load_region_map(cancer_index_path):
    """Return {provider_code: region} for codes with a real (non-England) region.

    Only providers carry a real region in the cancer data (ICBs are all
    "England"); we keep the filter generic (region present and != "England")
    rather than keying on level, so it stays correct if cancer's shape changes.
    """
    try:
        with open(cancer_index_path) as f:
            idx = json.load(f)
    except (OSError, ValueError):
        return {}
    out = {}
    for e in idx:
        code, region = e.get("code"), e.get("region")
        if code and region and region != "England":
            out[code] = region
    return out
