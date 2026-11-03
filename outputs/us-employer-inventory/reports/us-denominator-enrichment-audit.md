# US denominator and enrichment audit — November 3, 2026

Read-only recomputation from existing local/Azure Parquet extracts using the current canonical_company, identity_keys, geography and relevance functions. No database changes or filtering changes made.

## Corrected denominator

18,443 local + 4,549 Azure source rows; 22,763 canonical employer rows; 18,139 combined identities.

Geography and relevance cross-tab:
- US-evidenced, relevance screen passes: 1,127
- US-evidenced, relevance screen fails: 8,366
- Non-US/unresolved/conflicting, relevance screen passes: 1,244
- Non-US/unresolved/conflicting, relevance screen fails: 7,402

Thus the broader US-evidenced population is 9,493 combined identities. The 1,127 figure is an analytics-relevance subset, not the US total. The prior suggestion that the user's ~9k meant 9,014 raw source-dated records was unconfirmed; 9,493 is the relevant US denominator identified by this audit.

## Enrichment availability

| Field nonblank | Local / 18,443 | Azure / 4,549 |
|---|---:|---:|
| Requirements summary | 17,839 | 4,537 |
| Responsibilities summary | 18,341 | 4,537 |
| Technical tools summary | 7,684 | 1,311 |
| Country code | 1,201 | 3,911 |
| State | 17,003 | 4,448 |
| Original description | 18,342 | 4,537 |
| Source-reported date | 6,654 | 2,360 |
| Alive-check timestamp | 0 | 0 |

Nonblank does not establish correctness. State values include Locations, Hyderabad and Foster City. The export lacks enrichment_status and detailed classification-confidence fields, so full successful enrichment cannot be certified. Current role screening uses title and selected original/HTML text, not requirements/responsibilities/technical-tools summaries. Geography uses country, location text and limited ATS evidence; it does not simply trust structured state fields.

## Source-dated monthly US identities

| Month | All US-evidenced roles | Analytics subset |
|---|---:|---:|
| 2026-03 | 1 | 0 |
| 2026-04 | 62 | 22 |
| 2026-05 | 271 | 47 |
| 2026-06 | 835 | 97 |
| 2026-07 | 818 | 121 |
| 2026-08 | 535 | 74 |
| 2026-09 | 1,129 | 127 |
| 2026-10 | 771 | 102 |
| Source date missing | 5,071 | 537 |

Dates follow current builder policy (latest nonblank source-reported date per identity). These are historical posting observations, not verified current vacancies or employment growth. Do not merge created_at proxies into this series. The Azure raw dated series is concentrated in April–July 2026; local dated observations continue through October. Source-mix/collection changes and missing dates must accompany any month-over-month chart. The exports cover 15 named employers, not the full employability database or the whole industry.

## Interpretation

The broader 9,493 US identities should be distinguishable from the 1,127 analytics subset. Relevance should be visible as a selectable classification with audit reasons rather than described as the US denominator. Excluded examples include HR, sales territory management and government affairs as well as roles warranting further relevance review. Do not label all 8,366 excluded records analytics jobs without validation.
