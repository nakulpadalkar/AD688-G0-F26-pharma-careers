# Boston employer market

`data/employers.parquet` transcribes the 2026 headcount series on page 11 of MassBio's 2026 Industry Snapshot. All 20 values were checked against the rendered chart. `data/market-context.parquet` records statewide workforce context and the member-company geography on pages 6 and 37. The membership map was visually verified. These are different populations and years; do not divide the shortlist's workforce by statewide employment to claim a market share.

Run `python scripts/build_boston_market.py` to join this shortlist to the existing sanitized `database-jobs.parquet`. Quarto runs it before rendering. Run `python scripts/test_boston_market.py` to check geographic controls, source hashes, subset reconciliation and changed-input behavior.

The generated `web/` folder contains the public evidence include, calculated JSON and employer Parquet. Only these generated files are copied as website resources. Downloaded source PDFs, extracts, chart images and browser QA are ignored. The analysis never reads raw job descriptions or credentials and does not query either live database.

Geography deliberately requires explicit state evidence and a listed outreach municipality. Prefix-MA strings and city-only Cambridge are excluded; the public page documents that undercount. Commercial fit uses four saved relevance reasons; it is a rule-based screen, not manual assessment or a hiring promise. A company's absence from the 15-name inventory is missing coverage, not zero demand. AstraZeneca's posting coverage is narrower than the source's AstraZeneca/Alexion workforce grouping.

Company membership is a prospecting denominator only. The serviceable buyer count remains unknown until relevant teams, academic eligibility, budget and interest are validated. Calculator defaults and the 10/32/60 starter scenarios are assumptions. Pricing, delivery format and academic approval remain open decisions.
