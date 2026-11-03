# US employer explorer gates
- [x] G1: Only US postings are selectable; employer count is visible and no job cards appear before selection.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
  EVIDENCE: PowerShell in repository root; node scripts/test_dashboard.cjs exit 0. Eight independent pages, six US employers, no cards before selection, isolated company results, non-US rejection and selection reset verified.
- [x] G2: US downloads, skills, homepage and rendered pages agree.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
  EVIDENCE: PowerShell in repository root; quarto render exit 0 for eight pages; python scripts/verify_site.py exit 0 with 277 local links, fresh US download and derived skill analysis.
