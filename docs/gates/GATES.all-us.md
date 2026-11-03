# All US inventory gates
- [x] G1: Rebuild yields 9493 US identities, retaining all former 1127 analytics identities and date metadata.
  CHECK: python scripts/test_inventory.py
  EXPECT: INVENTORY_TESTS_OK
- [x] G2: Default UI shows all US jobs; relevance filters combine with other filters, pagination and yellow pull tags remain correct.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
- [x] G3: Eight pages render with consistent broader-inventory counts and labeled analytics scope.
  CHECK: quarto render
  EXPECT: Output created

Evidence: PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers. All checks exited 0. G1: INVENTORY_TESTS_OK and ALL_US_OK, previous 1127 IDs and dates preserved. G2: INTERACTIONS_OK, 9493 default, 1127 analytics, 8366 other, all-employer pagination and 5071 pull tags, combined relevance/level/signal/store filters. G3: Output created: _site/index.html, eight pages; verify_site.py EVIDENCE_OK with 282 local links and fresh assets. DOM fixture verification only; no browser visual check or deployment.
