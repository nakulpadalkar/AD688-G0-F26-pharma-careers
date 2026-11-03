# Pharma Career Intelligence

A static Quarto career explorer grounded in METEOR's saved pharma audit, primary employer pages, BLS 2025 wages/2025–2035 projections, NAICS industry context and O*NET tasks.

## Build without a server

```powershell
python scripts/build_site_data.py
quarto render
python scripts/verify_site.py
node --check scripts/dashboard.js
node scripts/test_dashboard.cjs
node scripts/test_ojs.cjs
python scripts/test_inventory.py
python scripts/test_site_metrics.py
uv run --with playwright python -X utf8 scripts/test_ojs_browser.py
```

The build uses saved evidence and requires no database connection or API keys. Growth & Pay and Skills use native Quarto/OJS modules; use the published website for these interactive pages. Direct-file loading does not initialize their module runtime reliably, and Observable libraries may require network access. The browser check above intercepts local asset requests without starting a server. Pushes to main trigger the existing GitHub Pages publication workflow.

## Refresh evidence intentionally

```powershell
python scripts/build_evidence.py --source-dir D:/Repositories/IndustryClassification/docs/research/pharma-demand
python scripts/build_site_data.py
quarto render
python scripts/verify_site.py
```

The source-dir is configurable. The input audit is a saved, historical read-only extraction. Refreshing its aggregate output does not recheck vacancies. Edit current-jobs.json only after reviewing employer-source content and recording live accessibility separately from indexed text; retain the actual review date and deadline status. The filename does not imply every role is open. Skill annotations distinguish required, preferred, alternatives and duties. Update benchmark years and source URLs together. Review text on the relevant QMD pages if a new snapshot changes counts or vintages.

The build publishes aggregate data and short annotated examples, never raw posting descriptions, credentials or database exports. Classification assignments in the source are not validated; they must not be treated as an industry/occupation census. Read `LESSONS.md` for this build's evidence limitations.

## Sources and content

- `outputs/site-reference/data/meteor.parquet`: historical counts, conservative geography, skills, monthly records, source hashes.
- `outputs/employer-page-review/data/current-jobs.parquet`: ten dated direct employer examples, including five indexed-only postings.
- `outputs/employer-page-review/data/reviewed-examples.parquet`: thirteen purposively reviewed historical examples.
- `outputs/site-reference/data/benchmarks.parquet`: official values with units, scope and URLs.
- `outputs/site-reference/data/usa_110m.parquet`: cached Plotly-compatible geometry copied from the classification reference project.
- `outputs/us-employer-inventory/web/dashboard-data.js` and `outputs/us-employer-inventory/web/evidence-tables.md`: reproducible generated assets.
- `outputs/site-reference/reports/verification.md`: validation receipt and limitations.

The four-course pathway follows the Pharma Certificate project's August 30, 2026 v2 syllabus draft. Work scenarios are editorial teaching examples. No graduate placement or salary-uplift claims are made.

## Quarto layout and HTML components

`index.qmd` includes `_includes/dashboard.html`; Quarto owns navigation, page layout and rendering. Data-driven HTML/JS is supplied by the component and the generated snapshot bundle. The desktop grid reserves 1,100 px for body content and 140 px each for the sidebar and margin, with 20 px gutters. The layout contracts responsively on narrower screens. Edit the component rather than generated `_site/*.html` files.

## Website pages

Home (`index.qmd`) is a compact introduction and page directory. `geography.qmd`, `outlook.qmd`, `jobs.qmd`, `skills.qmd`, and `work.qmd` each own one explorer. `about.qmd` describes the certificate; `eda_pharma.qmd` holds sources and methods. Shared footer and script includes live under `_includes/`. The navbar groups market pages and skills/work pages. Dashboard modules initialize only when their page elements exist.

Jobs and skills now use the direct employer sample. `build_site_data.py` derives `outputs/us-employer-inventory/curated/employer-analysis.parquet` from posting-level annotations. METEOR remains historical geography evidence; BLS remains market context. The database coverage audit is separate from the offline build; `scripts/audit_company_coverage.py --env-file <private-env-path> --alias local` (or `azure`) runs a bounded read-only audit and writes only aggregate operational receipts under `docs/`. Never publish environment files or connection details. See `outputs/employer-page-review/reports/direct-employer-review.md`.

The jobs explorer defaults to all US-located postings and supports employer and analytics-relevance filters. It shows the distinct employer count and per-employer posting counts. `outputs/us-employer-inventory/curated/us-jobs.parquet` is the US download; the original mixed-country source file is retained as a research archive. Skills use US-only scopes.

## Full database inventory (supersedes the six-example explorer)

The jobs and skills pages use `outputs/us-employer-inventory/curated/database-jobs.parquet` and `outputs/us-employer-inventory/curated/inventory-summary.parquet`. `outputs/us-employer-inventory/curated/us-jobs.parquet` is a build-generated copy for download. Original manual examples stay separate as research archives. Do not recreate the US inventory by filtering current-jobs.json.

Refresh with the environment containing psycopg2 and python-dotenv: `python scripts/fetch_inventory.py --env-file <private-path> --alias local`, then the same command with `--alias azure`, then `python scripts/build_inventory.py`. Fetches are read-only, all dates including null; raw extracts stay in ignored outputs/us-employer-inventory/raw. Run `python scripts/test_inventory.py`, render Quarto, then verify the site and dashboard interactions. Review outputs/us-employer-inventory/web/inventory-findings.md whenever source qualification counts change.

Career-level, data-product/dataset, store and search filters update the full inventory counts independently of employer selection. Select a company or All employers to show paginated cards. Counts describe stored, rule-screened posting identities, not live vacancies. See outputs/us-employer-inventory/reports/full-inventory-review.md and the public methods page.

## Task-scoped Parquet outputs

Canonical supporting data lives under outputs/, grouped by task: us-employer-inventory, employer-page-review, and site-reference. The active task has raw/ (local.parquet, azure.parquet; ignored and never published), curated/ (structured posting tables and summary snapshots), manifests/ (small JSON provenance and SHA-256 records), reports/, and web/ (generated JS and Markdown). Parquet uses Zstandard compression. Legacy heterogeneous reference documents retain exact original types in a compressed document column where needed; the main raw and posting tables have ordinary typed columns, including timestamp columns in raw snapshots.

The browser consumes the generated JS bundle. Download links expose curated Parquet only. Source-reported posting dates and database-created proxies remain separate. Raw-name counts include non-US/unrelated roles and overlapping records; all-employer-records.parquet retains sanitized metadata for every raw row.

## Acceptance gates

Task checklists and verification evidence are in [docs/gates](docs/gates/README.md). Run their checks from the repository root.

## Calculated website statistics

`quarto render` regenerates the saved statistics before rendering and checks their consistency afterward. `scripts/site_metrics.py` recalculates inventory, employer, qualification and date counts from the curated records. It derives BLS industry growth and CAGR from the saved employment endpoints; published occupational forecasts and wages remain source inputs.

The shared snapshot is `outputs/site-reference/data/site-metrics.parquet`. It stores display values, unrounded industry calculations, the calculation method and a hash of the evidence inputs. Generated `_variables.yml` supplies static Quarto content; `dashboard-data.js` carries the same snapshot alongside the records used by interactive filters. Do not edit generated numbers in HTML, `_variables.yml`, or the browser bundle. Update the source evidence and rebuild.

`python scripts/test_site_metrics.py` verifies saved snapshot, variables, browser bundle and rendered-page consistency, including changed-input controls. It runs as a Quarto post-render check, so a mismatch fails the render before publication.
