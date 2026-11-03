# Consistent calculated website metrics
- [x] G1: Counts derive from saved records; industry growth derives from endpoints; a saved metrics snapshot feeds page variables and browser data.
  CHECK: python scripts/test_site_metrics.py
  EXPECT: METRICS_OK
- [x] G2: Eight pages render with resolved data values; generated assets and interactions pass.
  CHECK: quarto render
  EXPECT: Output created
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK

Evidence: PowerShell, D:/Repositories/AD688-G0-F26-pharma-careers. All reviewed checks exited 0: METRICS_OK verifies saved snapshot/variables/bundle/rendered parity and changed-input controls; eight-page Quarto render invoked the post-render check successfully; EVIDENCE_OK verified 275 local links and fresh resources; INTERACTIONS_OK and INVENTORY_TESTS_OK / ALL_US_OK confirm 9493 US jobs, 1127 analytics, 5071 pulled-date proxies. Initial write failure recovered from the matching browser snapshot before rebuilding; subsequent checks passed. 2 gates met, 0 unmet, 0 abandoned. Not published; browser visual checks not performed.
