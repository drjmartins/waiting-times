"""
Export step: tidy DataFrame -> artefacts the static site consumes.

Outputs:
  site/data/index.json          - list of orgs (for the search/picker)
  site/data/org/<CODE>.json     - per-org time series for all standards
  site/data/national.json       - England series (used as comparison line)
  site/data/cwt_tidy.csv        - full tidy table for download / researchers
  site/data/meta.json           - build metadata + comparability note
"""
import json
import os
import datetime as dt

import pandas as pd

from . import config


def _org_payload(df_org):
    """Build the per-org JSON: one block per standard, 'All' breakdown only."""
    out = {"standards": {}}
    allrows = df_org[df_org["breakdown_type"] == "all"]
    for std in config.STANDARDS:
        s = allrows[allrows["standard"] == std].sort_values("month")
        if len(s) == 0:
            continue
        out["standards"][std] = {
            "label": config.STANDARDS[std]["label"],
            "target": config.STANDARDS[std]["target"],
            "months": s["month"].tolist(),
            "performance": s["performance"].tolist(),
            "within_target": s["within_target"].astype(int).tolist(),
            "total": s["total"].astype(int).tolist(),
            "data_status": s["data_status"].tolist(),
        }
    return out


def build(df, out_dir=config.SITE_DATA_DIR):
    os.makedirs(os.path.join(out_dir, "org"), exist_ok=True)

    # Per-org files + index
    index = []
    for (code, name, level), g in df.groupby(["org_code", "org_name", "org_level"]):
        payload = _org_payload(g)
        payload.update({"code": code, "name": name, "level": level})
        with open(os.path.join(out_dir, "org", f"{code}.json"), "w") as f:
            json.dump(payload, f, separators=(",", ":"))
        if level != "national":
            index.append({"code": code, "name": name, "level": level})
    index.sort(key=lambda r: r["name"])
    with open(os.path.join(out_dir, "index.json"), "w") as f:
        json.dump(index, f, separators=(",", ":"))

    # National series as its own file (comparison overlay)
    nat = df[df["org_level"] == "national"]
    if len(nat):
        code = nat["org_code"].iloc[0]
        national_payload = _org_payload(nat)
        with open(os.path.join(out_dir, "national.json"), "w") as f:
            json.dump(national_payload, f, separators=(",", ":"))

    # Tidy CSV for download
    df.sort_values(["org_code", "standard", "month"]).to_csv(
        os.path.join(out_dir, "cwt_tidy.csv"), index=False)

    # Metadata
    meta = {
        "built_at": dt.datetime.utcnow().isoformat() + "Z",
        "comparability_break": config.COMPARABILITY_BREAK,
        "n_orgs": len(index),
        "months": sorted(df["month"].unique().tolist()),
        "standards": {k: v["label"] for k, v in config.STANDARDS.items()},
        "note": ("31-day and 62-day standards changed in October 2023; figures "
                 "before that month are not directly comparable."),
    }
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return meta
