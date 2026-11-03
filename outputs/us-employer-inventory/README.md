# US employer inventory outputs

- `raw/local.parquet` and `raw/azure.parquet`: complete pinned name-matched extracts, including descriptions; private, git-ignored, never website resources.
- `curated/all-employer-records.parquet`: sanitized metadata for all 22,992 source rows, including overlaps and excluded records.
- `curated/database-jobs.parquet` and `curated/us-jobs.parquet`: 1,127 eligible US pharmaceutical data and analytics posting identities; the second is the browser-download alias.
- `curated/inventory-summary.parquet` and `curated/employer-analysis.parquet`: screening counts and derived skill observations.
- `manifests/`: small JSON extraction contracts, source hashes and artifact inventory.
- `reports/`: audit write-up and excluded-location review.
- `web/`: generated browser JS and rendered-table inputs. These are delivery artifacts, not the canonical data source.

Parquet compression: Zstandard. Raw timestamps have timezone-aware Arrow timestamp types. A database-created date is only a collection proxy and never substituted into the source-reported posting-date field. Dates on combined records use source-reported posting dates when available, otherwise the earliest database-created timestamp.

The 18,443 local and 4,549 Azure rows are not 22,992 distinct US analytics vacancies. The summary reconciles unrelated names, duplicate identities, non-US/unresolved geography and relevance exclusions. See the methods page for exact screening limitations.
