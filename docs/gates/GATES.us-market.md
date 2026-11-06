# US employer market gates
- [x] G1: Verify national firm/establishment counts and employment-size bands with dated primary sources; distinguish broader biopharma context.
  MANUAL: Inspect source definitions and extracted rows.
- [x] G2: Recompute nationwide employer and state posting evidence with missing geography, qualifications and provenance.
  CHECK: python scripts/test_us_market.py
  EXPECT: US_MARKET_OK
- [x] G3: Integrate US page and downloads; render and verify links without a server.
  CHECK: quarto render
  EXPECT: Output created
- [x] G4: Review results, source diff and AAR; clearly label historical evidence and assumed training demand.
  MANUAL: Inspect final page and outputs.

Evidence (PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers):
- G1: Downloaded Census source; retained exact national 3254 rows and SHA-256. Disjoint size bands sum to 2305 firms, 2882 establishments and 314242 industry employees. Verified latest-listed SUSB vintage and separately sourced PhRMA context.
- G2: test_us_market.py exit 0, US_MARKET_OK; aggregation, employer/state reconciliation, hashes, geography controls and changed-input checks.
- G3: quarto render exit 0, all ten pages, METRICS_OK; verify_site.py exit 0, 366 links; headless Edge US_BROWSER_OK, calculator changes/invalid/zero controls and mobile width. Desktop/mobile screenshots visually reviewed. No server.
- G4: Source diff --check exit 0; historical coverage, nonemployer/R&D exclusions, unknown buyers, and assumed enrollment clearly labeled. AAR recorded in LESSONS.md. No publication performed.

Completion: 4 met, 0 unmet, 0 abandoned.
