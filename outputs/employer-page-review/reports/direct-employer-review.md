# Direct employer review — November 2, 2026

Scope: replace the jobs/skills primary evidence with a purposive sample from pharmaceutical employers; retain BLS and historical geography. Ten postings from ten companies; six US, two Canada, one Mexico, one India. Five readable pages with application links; five indexed-only employer sources. No claim of representative skill prevalence or ten open vacancies.

## Source review ledger

| Company / requisition | Source access | Status | Source |
|---|---|---|---|
| AbbVie / R00152119 | Readable employer page | Application link observed | [Employer source](https://careers.abbvie.com/en/job/senior-analyst-national-data-operations-in-mettawa-il-jid-34718) |
| Iovance Biotherapeutics / 5464729008 | Readable employer page | Application form observed | [Employer source](https://job-boards.greenhouse.io/iovancebiotherapeutics/jobs/5464729008) |
| Amgen / R-256900 | Readable employer page | Application link observed | [Employer source](https://careers.amgen.com/es/trabajo/illinois/senior-manager-commercial-insights-patient-and-access-analytics/87/101379369120) |
| Takeda / R0193219 | Readable employer page | Application link observed | [Employer source](https://jobs.takeda.com/job/toronto/insights-and-analytics-manager/1113/102539792240) |
| Gilead Sciences / R0049331 | Readable employer page | Application link observed | [Employer source](https://gilead.yello.co/jobs/a_YVqH0ASpADAa5XKoSqyQ?locale=en) |
| AstraZeneca / R-258436 | Indexed employer posting; live body unreadable | Published deadline passed | [Employer source](https://astrazeneca.wd3.myworkdayjobs.com/Careers/job/US---Boston---MA/Associate-Director--Commercial-Data-Analytics---Reporting_R-258436) |
| Regeneron / R47203 | Indexed employer posting; live body unreadable | Application status unverified | [Employer source](https://regeneron.wd1.myworkdayjobs.com/en-US/Careers/job/Director--Customer-Master---CRM-Data-Management_R47203) |
| Pfizer / 4956634 | Indexed employer posting; live URL redirected | Posting URL redirects to search | [Employer source](https://www.pfizer.com/about/careers/job/4956634) |
| Novartis / REQ-10073039 | Indexed employer posting; live body unreadable | Published deadline passed | [Employer source](https://novartis.wd3.myworkdayjobs.com/en-US/Novartis_Careers/job/Conversational-Reporting---Analytics_REQ-10073039) |
| Sanofi / R2867765 | Indexed employer posting; live body unreadable | Published deadline passed | [Employer source](https://sanofi.wd3.myworkdayjobs.com/en-US/SanofiCareers/job/Data-Analyst_R2867765-1) |

## Database audit

Read-only repeatable-read queries against `met_career_match_jobposting`, with host-aware local/Azure selection, connection timeout, 180-second statement timeout and 3-second lock timeout. Sessions set UTC. Credentials remain in the external private environment file. SQL, regexes and window are in `scripts/audit_company_coverage.py`; aggregate receipts are `company-coverage-local.json` and `company-coverage-azure.json`. Only the aggregate table is included in the public methods page. No writes or sync were performed.

The audit covers posting dates from **January 1, 2025 through November 2, 2026 (UTC)**, across all geographies and active/inactive history. Employer labels are matched case-insensitively using whole-name tokens, including subsidiary labels containing those names. Counts are posting records, not unique vacancies or company-registry entries. Analytics counts use a broad title regex; a zero can reflect missing coverage or different titles, not no demand.

| Employer | Local records | Azure records | Local analytics-title records | Azure analytics-title records |
|---|---:|---:|---:|---:|
| AbbVie | 5,730 | 1,917 | 368 | 140 |
| Iovance Biotherapeutics | 40 | 9 | 3 | 1 |
| Amgen | 47 | 42 | 3 | 3 |
| AstraZeneca | 265 | 38 | 12 | 2 |
| Takeda | 75 | 56 | 0 | 0 |
| Gilead Sciences | 81 | 20 | 2 | 2 |
| Regeneron | 54 | 54 | 0 | 0 |
| Pfizer | 34 | 21 | 1 | 1 |
| Novartis | 94 | 60 | 5 | 0 |
| Sanofi | 23 | 15 | 2 | 2 |

All ten employers have matching posting records in both databases. Unequal counts do not establish data loss: the databases can have different collection and delivery coverage. Exact requisition matching and company-board registration were not audited.

## Validation

Quarto rendered all eight pages. `python scripts/verify_site.py` passed with 276 local links/anchors, independent geography controls, source/bundle equality and no duplicate DOM IDs. `node scripts/test_dashboard.cjs` passed all eight page initializations plus job country/status/level/search, missing salaries, CAD labeling, and three skill scopes. JavaScript syntax and source whitespace checks passed. Generated Quarto HTML retains renderer whitespace. No local server, browser visual review or deployment was performed.
