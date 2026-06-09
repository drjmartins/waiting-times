# Handoff: Cancer Waiting Times Explorer

I'm continuing a project that was scaffolded in another Claude session. The full
codebase is in this folder (unzipped from `cwt-dashboard.zip`). Please read this
note, then `README.md`, before doing anything.

## What this is

A static dashboard for NHS England Cancer Waiting Times (CWT) data, aimed at
researchers, clinicians and NHS analysts. Modelled loosely on OpenPrescribing:
pick an organisation (trust or ICB), see the three standards (28-day FDS, 31-day
combined, 62-day combined) as time series with a national comparison line and
target marker, plus a "size of the prize" calculator. Architecture is a
build-time Python pipeline feeding a static HTML/JS front end, deployed to GitHub
Pages via a daily GitHub Actions workflow.

## Project layout

- `pipeline/discover.py`   - scrapes the NHS CWT page, diffs links vs manifest
- `pipeline/normalise.py`  - maps source CSV columns -> canonical tidy schema;
                             applies the provisional->final revisions rule
- `pipeline/build_site_data.py` - emits per-org JSON, national.json, index.json,
                             cwt_tidy.csv, meta.json into `site/data/`
- `pipeline/synthetic.py`  - fabricated data generator for offline dev
- `pipeline/run.py`        - entry point: `--synthetic` or real run
- `site/index.html`        - the whole front end (self-contained)
- `.github/workflows/update-data.yml` - daily fetch + deploy

## CRITICAL: the data is currently synthetic

Everything in `site/data/` was built from FABRICATED numbers, because the
previous session's sandbox blocked network access to england.nhs.uk. The
synthetic generator was written to mimic the documented NHS column structure,
but the REAL column names have NOT been verified against a live file.

## The one caveat that will bite you

When you run the pipeline against the real NHS CSVs, the live file's column
headers may not match what `normalise.py` expects. The normaliser is designed to
fail loudly in that case, raising an error that names the missing field and
prints the columns it actually found. The fix is to add the real header names to
the `COLUMN_CANDIDATES` dict in `pipeline/normalise.py` (one place, by design),
then re-run. Same applies to `STANDARD_LABEL_MAP` if the standard labels differ.

Note also: NHS England changed the file format in Nov 2025, and the combined
provider flat files are being decommissioned from 11 June 2026 in favour of the
"Combined Provider and Commissioner (ICB based)" CSVs — those combined CSVs are
the intended source (one per financial year). The source page is:
https://www.england.nhs.uk/statistics/statistical-work-areas/cancer-waiting-times/

## Your first task

1. Install deps: `pip install -r requirements.txt`
2. Confirm the offline path works: `python -m pipeline.run --synthetic`, then
   serve `site/` (`python -m http.server 8099 --directory site`) and check the
   dashboard renders at http://localhost:8099.
3. Then do the real run: `python -m pipeline.run`. Expect it to fetch the
   combined CSVs and quite possibly fail on column mapping. Read the error, fix
   `COLUMN_CANDIDATES` (and `STANDARD_LABEL_MAP` if needed) against the real
   headers, and re-run until `site/data/` is rebuilt from genuine NHS data.
4. Sanity-check the output: do national 62-day figures land in a believable
   range, do real trust names/ODS codes appear in `index.json`, are recent
   months flagged provisional and older ones final?

Please start by reading the README and `pipeline/normalise.py`, then walk me
through what you find before making changes. Don't deploy anything yet — I want
to verify the real data looks right first.

## Things I'm keeping in the other session

Design and planning (UX, audience, what features to add next, visual design of
the charts) are being handled in a separate chat. Here in Claude Code I want to
focus on: getting real data flowing, troubleshooting the pipeline, testing the
GitHub Actions workflow, and deployment.

## Working agreement (two parallel sessions)

This project runs across two Claude sessions that CANNOT see each other. I (the
user) am the only link between them, carrying information by pasting it across.
Please follow this protocol so the two sessions don't contradict each other.

**Ownership split.** Decide things on the correct side of this line:

- *This session (Claude Code) owns:* pipeline internals (discover/normalise/
  build), the data store and schema, the GitHub Actions workflow, Git, testing,
  and deployment. Implementation and "how the data flows" decisions are yours.
- *The other session (planning/design) owns:* UX, audience, which features to
  build next, the visual design of charts and pages, and product wording.

When a recommendation crosses the line, don't just decide it — flag it. Say
explicitly: "this is a design/product call, recommend taking it to the planning
session," and give me a one-paragraph summary I can paste over. Example: choosing
a server-side pre-aggregation for a chart is your call; whether that chart should
be a funnel vs a percentile plot is the planning session's call.

**Decisions log.** Maintain a `DECISIONS.md` at the project root. Whenever either
session makes a significant decision, add a short dated entry. Keep entries to
~3 lines: what changed, why, date and which session. Read `DECISIONS.md` at the
start of each working session so you begin from current truth, not memory. If I
paste in a resolution from the planning session, record it there too. Create the
file if it doesn't exist yet; seed it with the key decisions already baked into
this codebase (static-site architecture, Oct-2023 comparability break handled in
UI, provisional→final revisions rule, size-of-the-prize as arithmetic gap only).

**Carry diffs, not descriptions.** When you want my/the other session's view on a
code change, the artefact that travels between sessions should be the actual diff
or full changed file, not a paraphrase — the judgement lives in the detail.
