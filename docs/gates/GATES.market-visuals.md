# Visual market explorer gates
- [x] G1: Read Azure Urban headline county observations with provenance, quality and missing values preserved; use correct units and geometry.
  MANUAL: Verify read-only transaction, year, source, scales, FIPS matches and exclusions.
- [x] G2: Replace table-led US/Boston market layouts with interactive maps and charts; keep evidence/downloads accessible.
  CHECK: python scripts/test_market_visuals.py
  EXPECT: MARKET_VISUALS_OK
- [x] G3: Render and test desktop/mobile selections, metrics, no-data states and existing calculator behavior without a server.
  CHECK: quarto render
  EXPECT: Output created
- [x] G4: Verify source/data regressions, review visuals and document AAR.
  MANUAL: Check browser screenshots, tests, links and source diff.

Evidence (PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers):
- G1: Azure read-only repeatable-read session verified. Headline file 11 / all / All; latest populated employment year 2024, 3144 source rows. 2025 5m Census boundaries joined exactly: 3144 nonterritory shapes, 2609 usable estimates, 535 missing, 2026 marginal/weak values hatched; no unmatched nonterritory source FIPS. Original bounds, quality, source commit/hash and license preserved. Units verified against official Urban dictionary.
- G2: test_market_visuals.py exit 0, MARKET_VISUALS_OK after final build; source hashes and US/Boston snapshots agree. KPI cards, state/county layers, county dropdown/zoom, size and employer bars, posting-subset chart and illustrative scenario cards implemented. Evidence tables remain collapsed and downloadable.
- G3: Final quarto render exit 0, 11 pages, METRICS_OK with no layout warnings. test_market_visuals_browser.py exit 0, MARKET_BROWSER_OK; existing US_BROWSER_OK and BOSTON_BROWSER_OK confirm both calculators. No server started.
- G4: US_MARKET_OK, BOSTON_MARKET_OK and EVIDENCE_OK (495 links) after render completion. Desktop/mobile screenshots reviewed, source diff --check exit 0. AAR appended to LESSONS.md; concurrent Parquet and training-overview changes preserved. No commit or publication performed by this task.

Completion: 4 met, 0 unmet, 0 abandoned.
