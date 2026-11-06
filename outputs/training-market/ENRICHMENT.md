# Scoped pending-enrichment runbook

The pinned cohort contains 279,358 records that were pending in the 357,230-record local pharma-candidate extract. The 79,358 figure from the companion request was a transcription discrepancy. The cohort includes non-US and unresolved candidates; it is not a verified US pharma-employer list.

The local PostgreSQL scan and offline screening have executed. The production stage runner is prepared and plan-tested only. No database enrichment statuses were changed by this task. The employability repository requires script-only execution: the user launches the command below.

## Preview the exact scope

```powershell
python D:/Repositories/AD688-G0-F26-pharma-careers/scripts/run_pharma_enrichment.py
```

## Run the first bounded batch

```powershell
python D:/Repositories/AD688-G0-F26-pharma-careers/scripts/run_pharma_enrichment.py --execute --python D:/Repositories/met-employability-services/.venv/Scripts/python.exe --max-batches 1
```

The first invocation attempts 100 pinned IDs. Repeat to advance through unattempted batches, or increase `--max-batches` after reviewing the first receipts. Add `--retry-partial` to revisit incomplete batches. Completed stages are not repeated. Partial outcomes and unresolved fields remain recorded; a stage attempt is never counted as full enrichment. Existing job-stage validation and local advisory leases remain in effect. No Azure delivery, global backlog selection, global repair, status reset or network HTML capture is launched. Missing saved evidence can therefore remain unresolved.

Receipts are immutable and saved under `outputs/training-market/enrichment/runs/`. Do not delete them to force a successful status. Source IDs and hashes are pinned in `pending-ids.json` and `manifest.json`. Stage-entrypoint code changes stop resume for review. The existing service runner also records its code identity.

## Readback coverage

Use `scripts/audit_pharma_enrichment.py --env-file <private-local-env-path> --label after` against the exact pinned IDs after a run. Coverage receipts are immutable; preserve each before/after comparison in a separate run root when making a later comparison. A nonempty code or summary is coverage evidence, not independent accuracy validation. No salary or BLS value is imputed where source evidence is absent.

## Baseline field coverage

| Field | Nonempty among pinned IDs |
|---|---:|
| enrichment_status | 279,358 |
| naics_code | 3,258 |
| soc_code | 2,262 |
| onet_code | 2,413 |
| requirements_summary | 275,073 |
| bls_annual_median_wage | 2,100 |
| bls_source_year | 2,260 |
| posted_at | 166,019 |
| countryiso | 35,904 |
| state_code | 76,215 |
| jobhive_company_id | 170,394 |
| technical_tools_summary | 110,776 |
| alive_checked_at | 299 |
| annual_salary_min | 4,138 |
| annual_salary_max | 4,102 |

All 279,358 pinned IDs were found. Baseline statuses: pending=279,358.

Additional employer verification, trusted reference-code assignment, salary interpretation and full occupation/skill enrichment belong to the production stage workflow. The offline website screen does not pretend to complete those stages.
