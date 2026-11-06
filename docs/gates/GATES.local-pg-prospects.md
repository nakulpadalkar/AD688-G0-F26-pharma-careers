# Broad local PostgreSQL employer and early-career evidence
- [x] G1: Read-only extraction scans all available dates and employers; saves query, row counts and source hashes, with missing posting dates retained.
  MANUAL: Inspect extraction receipt, transaction flag and streamed totals.
- [x] G2: Deduplicated employer/US/analytics/early-career evidence reconciles; age is not experience and missing evidence remains unknown.
  CHECK: python scripts/test_training_market.py
  EXPECT: TRAINING_MARKET_OK
- [x] G3: Saved prospect data and website page expose scope, confidence, freshness, skills and traceable examples.
  CHECK: quarto render
  EXPECT: Output created
- [x] G4: Review results and AAR; report actual processed coverage and limitations.
  MANUAL: Inspect final summary and source diff.

Evidence: PowerShell at repository root. Read-only REPEATABLE READ extraction processed all 10,654,778 rows through the candidate predicate and saved all 357,230 matches with hash receipt. TRAINING_MARKET_OK and SCOPED_RUNNER_OK exit 0. Existing service runner --plan verified exactly 100 pinned IDs and local-only target without executing production stages. Quarto rendered 11 pages, METRICS_OK passed, verify_site.py EVIDENCE_OK checked 485 local links and fresh public resources. Result: 124,101 US candidate identities, 5,822 analytics-title matches across 1,254 employer labels, 589 early-career review signals and 100 student pathways. 279,358 pending IDs pinned and read back; none marked complete by this task. Full production enrichment delivered as prepared user-run script under existing rule. Validation receipt: outputs/training-market/validation.json. 4 gates met, 0 unmet, 0 abandoned. No website publication or browser visual check.
