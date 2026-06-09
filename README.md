# Cancer Waiting Times Explorer

A user-friendly, static dashboard for NHS England Cancer Waiting Times data,
aimed at researchers, clinicians and NHS analysts. Inspired by the structure of
OpenPrescribing: pick your organisation, see the standards as time series with a
national comparison and target line, and download the tidy data.

## How it works

```
NHS England CWT page
   │  (daily check; acts only on new/revised files)
   ▼
pipeline/discover.py   scrape links, diff against data/manifest.json
   ▼
pipeline/normalise.py  map source columns -> canonical tidy schema,
                       apply provisional→final revisions rule
   ▼
data/processed/tidy.parquet   accumulated full tidy table
   ▼
pipeline/build_site_data.py   per-org JSON + national.json + index.json
                              + cwt_tidy.csv (download) + meta.json
   ▼
site/  static front end (index.html) — deploy to GitHub Pages / Cloudflare Pages
```

The monthly refresh and deploy are automated by
`.github/workflows/update-data.yml` (daily cron + manual trigger).

## Design decisions worth knowing

- **Static site, no backend.** Data changes monthly, so a build-time pipeline
  feeding static files is cheaper, faster and more secure than a live server.
- **October 2023 break is explicit.** 31-day and 62-day standards changed then
  and are not comparable across that line; the UI defaults to data from 2023-10
  and labels the discontinuity rather than splicing one continuous series.
- **Revisions are first-class.** Provisional months get overwritten as they are
  revised; `final` always beats `provisional` for the same period/org/standard.
- **Format changes fail loudly.** NHS changed the file layout in Nov 2025.
  `normalise.py` maps a list of candidate column names per field and raises a
  clear error if a required field can't be mapped — so CI catches the next change.
- **"Size of the prize" is honest.** v1 shows the arithmetic gap (extra patients
  per month at a chosen target), explicitly *not* a modelled clinical outcome.
  A survival/economic module can be layered on later as a separate, caveated step.

## Run it

```bash
pip install -r requirements.txt

# Offline demo with fabricated data (no network needed):
python -m pipeline.run --synthetic
cd site && python -m http.server 8099   # open http://localhost:8099

# Real run (requires network access to england.nhs.uk):
python -m pipeline.run
```

## Important caveat on the prototype

The committed `site/data` is built from **synthetic, fabricated numbers** for
development. Real figures appear only after a successful `python -m pipeline.run`
against the live NHS England source.

Data source: NHS England Cancer Waiting Times statistics, Open Government
Licence v3.0.
