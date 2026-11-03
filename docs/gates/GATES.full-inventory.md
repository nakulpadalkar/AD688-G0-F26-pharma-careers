# Full US employer inventory gates
- [x] G1: Read all matching employer records from local PostgreSQL and Azure without an arbitrary date or row cap; record read-only receipts and source counts.
  EVIDENCE: read-only manifests in outputs/us-employer-inventory/manifests; 18,443 local + 4,549 Azure rows; no date/row cap.
- [x] G2: Reconcile cross-store identities, screen US geography and role relevance with auditable exclusions, and assess vendor/data, experience and degree evidence.
  CHECK: python scripts/test_inventory.py
  EXPECT: INVENTORY_TESTS_OK
- [x] G3: Employer-first explorer, per-company counts, pagination, skills and methods use the combined inventory and distinguish historical records from live checks.
  CHECK: node scripts/test_dashboard.cjs
  EXPECT: INTERACTIONS_OK
- [x] G4: Render all pages, validate counts/links/assets, inspect findings and record AAR.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK

- [x] G5: Supporting data is in task-scoped compressed Parquet; all raw records reconcile and real posting dates are distinguished from creation-date proxies.
  CHECK: python scripts/test_inventory.py
  EXPECT: INVENTORY_TESTS_OK

Final evidence: isolated Quarto render of 8 pages succeeded; final repository inventory, interaction and 282-link checks passed. AAR recorded in LESSONS.md. Receipt: outputs/us-employer-inventory/reports/validation-receipt.json. No external deployment.
