# Parquet and visual-market release verification

- [x] G1: Fetch all branches and review source updates, stashes and cleanup candidates.
  MANUAL: Git refs/status and current build inputs inspected.
- [x] G2: All eleven pages, Parquet migration, data and frontend/browser checks pass.
  MANUAL: Reviewed offline render, Python and Node checks, and Edge headless browser suites.
- [x] G3: Preserve source and output changes in targeted commits; remove temporary artifacts and exclude private data.
  MANUAL: Staged paths and diff checks inspected.
- [ ] G4: Main and gh-pages publication succeed; local main synchronized and working tree/stashes empty.
  MANUAL: Verify remote HEAD, Git status, Quarto Publish and Pages deployment results.

Evidence: PowerShell, repository root. Fetch all/prune succeeded; main current before commits, gh-pages remains publication-only. No stashes, symlinks or running previews. Quarto rendered 11 pages; inventory, site, metrics, Boston, US, training-market, market-visuals and mocked-runner checks exited 0. EVIDENCE_OK verified 495 links; PARQUET_SITE_OK verified formats and snapshot/homepage parity. All three JS syntax checks, two Node suites and four Edge headless browser suites passed, including county/state selection, missing estimates, disclosures and mobile layout. No database refresh or local server started. Temporary screenshot trees removed after verification.

G3 evidence: reviewed source and generated-site commits; source whitespace and staged-path checks passed. Superseded CSV/JSON datasets deleted by migration, temporary QA removed, ignored private data preserved. Generated Quarto whitespace retained. README command block and metrics explanation corrected; AAR lesson saved.
