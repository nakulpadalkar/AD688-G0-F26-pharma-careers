# SCSS modularization gates
- [x] G1: Ordered SCSS modules preserve every existing CSS rule and declaration.
  CHECK: python artifacts/scss-migration/check.py
  EXPECT: SCSS_OK
- [x] G2: Eight Quarto pages compile and use the SCSS theme; local assets and interactions remain valid.
  CHECK: quarto render
  EXPECT: Output created
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK

Evidence: PowerShell at D:/Repositories/AD688-G0-F26-pharma-careers; all commands exited 0. SCSS_OK preserved every original selector/declaration in order across 14 modules. Quarto rendered eight pages. EVIDENCE_OK checked shared compiled theme, component selectors and 274 local links; INTERACTIONS_OK checked all eight page initializations and existing interactions. git diff --check passed. No browser visual check or deployment performed. Gates: 2 met, 0 unmet, 0 abandoned.
