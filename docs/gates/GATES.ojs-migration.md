# Gates: Native Quarto analytics migration

Scope: Growth & Pay and Skills only; retain shared branding and evidence definitions.
Plan: export focused data, migrate both pages, style native components, verify render and interactions.

- [x] G1: Both native OJS pages render and site metrics remain consistent.
  CHECK: quarto render
  EXPECT: METRICS_OK
  EVIDENCE: PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers; quarto render exit 0; 8 pages and METRICS_OK after final page/style changes.
- [x] G2: OJS filtering, measures, source selection and compiled runtime are verified.
  CHECK: node scripts/test_ojs.cjs
  EXPECT: OJS_OK
  EVIDENCE: PowerShell, repository root; node scripts/test_ojs.cjs exit 0; OJS_OK. Focused attachment parity and every skill/source denominator independently reconciled with curated jobs.
- [x] G3: Other dashboard pages and local links retain their behavior.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
  EVIDENCE: PowerShell, repository root; node scripts/test_dashboard.cjs exit 0; INTERACTIONS_OK. Existing jobs, map, scenarios and independent page guards pass.
- [x] G4: Rendered local links resolve.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
  EVIDENCE: PowerShell, repository root; python scripts/verify_site.py exit 0; EVIDENCE_OK; 329 local links and anchors, fresh data assets and shared compiled theme.
- [x] G5: Browser interactions and mobile containment pass without a local server.
  CHECK: uv run --with playwright python -X utf8 scripts/test_ojs_browser.py
  EXPECT: OJS_BROWSER_OK
  EVIDENCE: PowerShell, repository root; uv run --with playwright python -X utf8 scripts/test_ojs_browser.py exit 0; OJS_BROWSER_OK. Edge headless request interception, no server; 2 pages, 3 measures each, 3 skill scopes, sorting, source parity, focus, empty/recovery states, desktop and 390px mobile; zero runtime errors.
- [x] G6: Review responsive styling, evidence context and diff; record verification limits and AAR.
  EVIDENCE: Reviewed final desktop/mobile screenshots in artifacts/ojs-migration, data definitions and source links; git diff --check passed for changed tracked source files. Existing user edits preserved. AAR recorded in LESSONS.md. Browser check uses intercepted local assets, not deployed hosting; no deployment performed.
