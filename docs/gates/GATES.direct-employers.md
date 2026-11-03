# Direct employer evidence gates
- [x] G1: Expand to at least eight companies with traceable directly reviewed postings, dates and skill evidence; distinguish unavailable pages.
  EVIDENCE: Manual source review in docs/direct-employer-review.md: 10 companies, 10 distinct requisitions, URLs and skill annotations. Five readable application-link pages and five explicitly indexed-only employer sources; dated status and missing criteria retained.
- [x] G2: Jobs and skills use the direct sample, with denominators, company breadth and source links; BLS remains market context.
  EVIDENCE: PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers, python scripts/verify_site.py exit 0: EVIDENCE_OK, 276 local links/anchors; fresh source-derived skill scopes (10 all / 6 US / 5 readable). BLS unchanged.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
- [x] G3: Query local PostgreSQL and Azure read-only for sampled employers; record scope, matches and limitations without credentials.
  EVIDENCE: scripts/audit_company_coverage.py exits 0 for local and azure, each transaction read-only/repeatable-read with UTC session. Both receipts show positive employer posting counts for all 10 companies. Scope and exclusions in docs/direct-employer-review.md; no database writes.
- [x] G4: Render and verify independent pages and interaction regressions; record AAR.
  EVIDENCE: PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers: quarto render exit 0 for 8 pages; node scripts/test_dashboard.cjs exit 0 INTERACTIONS_OK for 8 independent pages, country/currency/status and skill filters; node --check exit 0. AAR appended to LESSONS.md. No server, browser visual review or deployment.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
