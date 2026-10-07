"""Stamp `updates_paused: true` into both dashboards' meta.json.

Run by the workflow ONLY on the manual publish path (skip_fetch). The pages show
"Automatic updates are currently paused." whenever their meta.json carries this
flag. Because a normal fetch run rebuilds meta.json from scratch and never sets
it, re-enabling the scheduled cron removes the note automatically — no HTML edit
is needed to un-mothball.
"""
import json
import os
import sys

META_PATHS = ("site/cancer/data/meta.json", "site/rtt/data/meta.json")


def stamp(paths=META_PATHS):
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(f"{missing} missing — nothing to publish, refusing to stamp")
    for path in paths:
        with open(path) as f:
            meta = json.load(f)
        meta["updates_paused"] = True
        with open(path, "w") as f:
            json.dump(meta, f, indent=2)
        last = meta["months"][-1] if meta.get("months") else "n/a"
        print(f"  stamped updates_paused in {path} (data to {last})")


if __name__ == "__main__":
    try:
        stamp()
    except Exception as e:
        print(f"freeze_note failed ({e}).", file=sys.stderr)
        sys.exit(1)
