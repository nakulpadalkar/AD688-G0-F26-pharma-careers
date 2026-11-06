# Broad local PostgreSQL training-market evidence

The extraction scans the entire local posting table in a read-only, repeatable-read transaction. It retains all dates and missing posting dates. The row-level candidate predicate covers pharma, biotech, life sciences and clinical research text or NAICS 3254/541714; it is not a verified employer registry or a complete market census.

- `receipt.json`: exact query, scope, snapshot counts and raw SHA-256.
- `raw/local-candidates.parquet`: private source evidence, ignored by Git and excluded from website resources.
- `processed/postings.json`: locally retained sanitized identity and classification evidence, excluded from publication.
- `web/summary.json`: calculated public aggregates and provenance.
- `web/employer-prospects.csv`: employer-label counts, early-career review signals, skills and source example.
- `web/analytics-postings.csv`: US analytics matches with career signals, date provenance and stored URLs.
- `web/evidence.qmd`: generated website content; never edit counts by hand.

Refresh explicitly, from the repository root:

```powershell
python scripts/fetch_training_market.py --env-file <private-local-env-file>
python scripts/build_training_market.py
python scripts/test_training_market.py
quarto render
python scripts/verify_site.py
```

Normal Quarto builds use the saved public evidence and do not connect to PostgreSQL. Industry and qualification screening requires individual review. Missing requirements are unknown, internships are separate, and age/tenure phrases are excluded from experience. Employer names are normalized only for case/whitespace; corporate-family consolidation is not claimed. The original 15-employer inventory is a separate snapshot and cannot be added to these totals.
