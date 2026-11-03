# Multipage Quarto navigation gates
- [x] G1: Each explorer has its own QMD page and home provides links, preserving 1000px body width.
  CHECK: quarto render
  EXPECT: Output created
- [x] G2: Every page loads independently; map, job and scenario interactions still work.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
- [x] G3: All rendered local links/anchors and evidence snapshots remain valid.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK

Evidence: PowerShell in repository root; quarto render, node scripts/test_dashboard.cjs and python scripts/verify_site.py all exit 0. Eight rendered pages, eight independent page initializations, 274 local links/anchors. All 3 gates met; 0 unmet, 0 abandoned. Browser visual QA not claimed.
