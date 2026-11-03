# Website prose revision
- [x] G1: Public pages explain the evidence and career relationship without build instructions, editorial notes or revision history; all counts and citations preserved.
  MANUAL: Review page sources and generated copy; compare inventory and benchmark data before and after.
- [x] G2: All eight pages render and local links and data equality pass.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
- [x] G3: Existing filters, skill interactions and scenarios still work.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK

Evidence: Reviewed public source copy and generated findings; 1,127 postings / 13 employers unchanged. Eight-page Quarto render exit 0. PowerShell repository-root verify_site.py and test_dashboard.cjs exit 0 with expected tokens; 282 local links. Hash-checked source snapshot copied to local _site. Three gates met; zero unmet or abandoned. AAR logged in LESSONS.md.
