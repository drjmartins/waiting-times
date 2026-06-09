# Live-tool copy: footer + methods notes

Replaces the now-false "Prototype built on synthetic data" footer. Two pieces:
a short footer for every page, and a longer methods block for an About panel or
the foot of the comparison page. Written for a research/clinician/analyst
audience: accurate, caveated, citable. British English, no em dashes.

Placeholders in {curly braces} should be filled programmatically by the build
(Code's side) from meta.json so they never go stale.

---

## Short footer (every page)

Data source: NHS England Cancer Waiting Times statistics, published monthly and
used here under the Open Government Licence v3.0. This dashboard is an independent
tool and is not affiliated with or endorsed by NHS England.

Data to {latest_month}. Last updated {build_date}. Figures for the most recent
months are provisional and subject to revision.

The 31-day and 62-day standards changed in October 2023; figures before that
month are not directly comparable and are shown separately.

---

## Methods note (About panel / comparison-page foot)

### What this shows

Performance against the three operational cancer waiting-times standards: the
28-day Faster Diagnosis Standard, the 31-day combined standard (decision to treat
to first treatment), and the 62-day combined standard (referral to first
treatment). Data are NHS England's published provider and commissioner figures,
rebuilt automatically each month from the source files.

### Comparison period

The trust comparison pools the most recent three months of finalised data
({compare_window}). Numerators and denominators are summed across those months
and performance is computed from the totals, rather than averaging monthly
percentages, so larger months are weighted correctly. Provisional months are
shown in individual trust trends but are not used as the comparison basis, so a
trust's comparative position does not shift as provisional data is revised.

### Funnel limits and overdispersion

The funnel plot shows each trust's performance against the volume of patients in
scope. Control limits indicate how far a trust would be expected to sit from the
national figure. By default the limits include an overdispersion adjustment
(after Spiegelhalter), which widens them to reflect genuine, structural variation
between trusts that exceeds simple random variation. Without this adjustment, the
plain binomial limits flag a large proportion of trusts as outliers, because they
assume all trusts are otherwise identical, which they are not. An unadjusted
(binomial) view is available via the toggle for comparison. A trust outside the
limits is unusual relative to others given its volume; it is not, on its own,
evidence of good or poor care.

### Reliability threshold

Trust-periods with fewer than 10 patients in scope are treated as too small for a
reliable performance estimate. Such trusts appear on the funnel only, where their
low volume is shown explicitly by the widening limits, and are excluded from the
percentile view, where a small denominator would produce a misleadingly precise
rank.

### Scope and fallback

Trusts can be compared across all of England or within one of the seven NHS
England regions. Where too few trusts in a region meet the reliability threshold
for the selected measure, the view widens automatically to England and says so.
Two providers that are national services rather than regional (a rapid
investigation service and an independent-sector hospital) appear in the England
view only.

### Important caveats

These are trust-level, aggregated figures. Differences between trusts can reflect
case mix, the local population, data recording practices, and service
configuration, not only the timeliness of care. Associations shown here do not
establish cause. Figures depend on trust reporting and pathway coding, which can
vary. This tool is for understanding patterns and prompting questions, not for
ranking or judging individual organisations.

### Citation

NHS England Cancer Waiting Times statistics, {data_range}. Accessed via
[dashboard name] on {build_date}. Underlying data: Open Government Licence v3.0.
