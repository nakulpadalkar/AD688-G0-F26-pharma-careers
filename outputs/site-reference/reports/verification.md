# Verification receipt — November 2, 2026

Working directory: D:/Repositories/AD688-G0-F26-pharma-careers
Shell: PowerShell 7; Python 3.12; Quarto 1.11.1; Node.js available on PATH.

- Quarto renders index, evidence/methods and certificate pages. Pre-render rebuilds bundled data from checked local snapshots only.
- verify_site.py reconciles 1,353 historical candidates, 21 month bins, 654 mapped records and 51 state/DC entries. Eleven positive/negative geography controls pass. Generated bundles match source JSON; 85 local links and anchors resolve; no raw candidate/audit files or credentials are in the generated website.
- test_dashboard.cjs executes dashboard.js with a minimal DOM fixture. Checked/historical switching (2/13 examples), title/skill search, empty state, career levels, all three choropleth measures, keyboard state selection, reset, and three work scenarios pass. This is interaction-logic coverage, not a browser or layout test.
- JavaScript syntax check passes. Source diff whitespace check passes. Generated Quarto HTML contains template trailing whitespace; generated framework assets change with this installed Quarto version.
- Map geometry bounds are inside its SVG viewBox; all 51 data keys match state metadata. Responsive CSS includes 950px and 600px breakpoints, focus styles, reduced-motion and print rules. Visual appearance remains unverified.

## Browser limitation

The supported browser rejected the local file URL because its security policy permits only HTTP/HTTPS. No alternate browser route was attempted. The user's standing instruction prohibits starting local servers without an explicit request. Therefore no live browser, screenshot or mobile visual QA was performed. Open `_site/index.html` manually to review the rendered site.

## Evidence boundaries

The current-job section contains two selected employer pages with application controls observed November 2, 2026. It is not an exhaustive US vacancy count, and checks do not refresh automatically. Historical METEOR records are not presented as current jobs. BLS uses 2025 wages and 2025–2035 projections. Assigned NAICS/SOC codes are not validated. No graduate placement, salary uplift or causal certificate outcomes were supplied.

## Delivery

Source and generated site saved locally in the existing Quarto repository. No local server, database mutation, commit, push, pull request or deployment was performed. The existing GitHub Pages workflow is preserved.

## Multipage update

Eight QMD pages render successfully. The original long dashboard is split into a short home directory, geography, outlook, jobs, skills, work, certificate and sources. The 1000px body and 140px side columns are preserved. Verification checks 274 local links/anchors and independent initialization on all eight pages, alongside the existing interaction checks. First render reported a missing generated Bootstrap asset; an unchanged rerender completed successfully. Browser visual QA remains unverified under the previously recorded limitation.
