# Restore familiar visuals with native OJS

- [x] G1: Full Quarto render preserves shared metrics.
  CHECK: quarto render
  EXPECT: METRICS_OK
  EVIDENCE: PowerShell, repository root; quarto render exit 0, all 8 pages and METRICS_OK.
- [x] G2: Data and existing dashboard regressions pass.
  CHECK: node scripts/test_ojs.cjs
  EXPECT: OJS_OK
  EVIDENCE: PowerShell, repository root; node scripts/test_ojs.cjs exit 0, OJS_OK; independent source and denominator parity.
- [x] G3: Browser verifies bubbles, card measures, evidence, focus, empty states and mobile layout.
  CHECK: uv run --with playwright python -X utf8 scripts/test_ojs_browser.py
  EXPECT: OJS_BROWSER_OK
  EVIDENCE: PowerShell, repository root; uv run --with playwright python -X utf8 scripts/test_ojs_browser.py exit 0, OJS_BROWSER_OK; real Edge, 3 scopes/measures, click/keyboard/focus, proportional areas and stable search scale, source filtering, empty states, 390px mobile; no server.
- [x] G4: Existing dashboards and site links pass; screenshots reviewed and AAR recorded.
  EVIDENCE: PowerShell, repository root; node scripts/test_dashboard.cjs exit 0 INTERACTIONS_OK; python scripts/verify_site.py exit 0 EVIDENCE_OK (348 local links). Desktop/mobile screenshots reviewed in artifacts/ojs-restored-visuals. AAR appended to LESSONS.md. No deployment; unrelated Boston-market files left untouched.
