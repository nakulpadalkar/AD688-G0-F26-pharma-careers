# Expanded pharmaceutical data inventory
- [x] G1: Include pharmaceutical data/analytics pathways beyond commercial roles, with positive and negative controls.
  CHECK: python scripts/test_inventory.py
  EXPECT: INVENTORY_TESTS_OK
- [x] G2: Regenerate all counts, skills and downloadable Parquet from expanded inventory; verify rendered pages.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
- [x] G3: Independent filters and complete pagination work with expanded inventory.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK

Evidence: PowerShell in repository root; all three checks exit 0 with expected tokens. 1,127 identities, 13 employers. Isolated eight-page Quarto render exit 0; 282 links verified; current source hashes checked before copying local _site. AAR recorded in LESSONS.md. 3 met, 0 unmet, 0 abandoned.
