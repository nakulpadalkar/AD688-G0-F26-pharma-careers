# Parquet-only website data
- [x] G1: Migrate market inputs, calculated snapshots and downloads with exact value preservation; keep operational receipts separate.
  CHECK: python scripts/test_training_market.py
  EXPECT: TRAINING_MARKET_OK
- [x] G2: Rebuild all pages and verify counts, Parquet links and no CSV/Excel dataset downloads.
  CHECK: quarto render
  EXPECT: Output created
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK

Verified 2026-11-06: all four market data checks passed; full Quarto render completed for 11 pages; EVIDENCE_OK checked 495 links; PARQUET_SITE_OK verified formats, snapshot parity and calculated homepage counts. No CSV/XLSX/XLS files remain in _site. Public deployment not verified in this task.
