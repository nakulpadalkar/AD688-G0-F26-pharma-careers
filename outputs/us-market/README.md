# US employer market evidence

`data/census-3254.parquet` retains the original 26 national NAICS 3254 rows from the Census 2022 SUSB detailed enterprise-size dataset, its URL, encoding and whole-download SHA-256. Read the downloaded text as Windows-1252. The broad source file is ignored; the selected public rows are versioned.

`scripts/build_us_market.py` aggregates disjoint enterprise-size bins; total and overlapping subtotal codes 01, 33 and 37 are not added as bins. Firms, establishments and industry employment remain separate. Counts exclude nonemployers. Enterprise employment determines size while the employment column counts the selected industry's establishments. Do not sum firm counts across industries/states or treat the manufacturing population as all biopharma buyers.

The builder reuses saved sanitized posting identities, commercial-fit rules and conservative state parsing from the existing project. It does not fetch the database or infer US workforce from job counts. Generated public outputs in `web/` include all 15 employer counts, all states plus unallocated geography, Census bands and input hashes. `python scripts/test_us_market.py` verifies aggregation, changed-input controls and source parity.

The page also cites the PhRMA summary of the 2024 TEConomy economic footprint, reviewed November 6, 2026. This broader estimate includes Puerto Rico and is separate from Census's national manufacturing series. Scenarios are unvalidated assumptions; no buyer commitments, fees or program approval are implied.
