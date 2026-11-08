# Lessons

Written by /aar-loop after each session's After Action Review. Read this file before starting a new task in this project. Every entry should be concrete and checkable, never vague.

## 2026-11-02 -- In the saved pharma audit, countryiso is blank for 1326 of 1353 commercial candidates; retain explicit exclusions for foreign records and known corrupt locations such as Hyderabad, Indiana. Only 654 records map conservatively to states. Keep historical counts separate from dated employer application-page checks and from BLS employment projections.
- Expected: Build a modern pharma career website grounded in METEOR and official labor statistics.
- Actual: Three static Quarto pages built with traceable aggregates, two checked employer examples, thirteen historical examples and interactive choropleth. Browser file URL was blocked; static and simulated-DOM checks passed.
- Why: Source geography and classification fields are incomplete or inconsistent, and the supported browser disallows file URLs. The no-server instruction prevents local HTTP preview. Geography exclusions, source vintages and verification limits remain visible. No standing-rule fix proposed.
- tags: pharma,geography,website,evidence

## 2026-11-02 -- When moving dashboard sections into separate QMD pages, guard each JavaScript module by its own DOM container and test each rendered page independently with absent elements returning null. Keep home as a directory and verify cross-page anchors after moving sections.
- Expected: Replace the long-scrolling dashboard with focused website pages.
- Actual: Eight Quarto pages render; 274 local links and anchors and eight independent page initialization tests pass.
- Why: The original dashboard assumed all containers existed on one page. Module-level guards preserve interactions after splitting content. A transient missing Bootstrap asset on first render resolved on unchanged rerender; no standing-rule change proposed.
- tags: quarto,navigation,javascript

## 2026-11-02 -- For direct employer samples, store source_access and availability separately: Workday can expose indexed job text while the live page has no readable body, and Pfizer job URLs can redirect to search. Use application_observed only for readable pages with an observed application control; exclude indexed-only rows from the readable skills scope. Keep country and currency explicit for overseas roles supporting US teams.
- Expected: Expand direct pharma jobs and skills evidence and verify company presence in local PostgreSQL and Azure.
- Actual: Ten employers annotated, five readable application-link pages and five indexed-only sources; all ten employers found in both databases through read-only queries. Eight rendered pages, 276 links and interaction checks pass.
- Why: Indexed descriptions can outlive application deadlines or readable pages. Separate source access, status and geographic scopes prevent stale roles or overseas salaries from being presented as current US openings. No standing-rule fix proposed.
- tags: employer-sources,freshness,postgres,azure

## 2026-11-02 -- For the US employer selector, test zero job cards before selection and after clearing selection, employer-isolated results, and rejection of a non-US employer value. Derive employer counts and the US download from country=US, not from US-team wording.
- Expected: US-only job explorer showing employer counts and cards after company selection.
- Actual: Six US employers and six postings; two US skill scopes; eight-page render, 277 links and selector regressions passed.
- Why: No remaining gap. Explicit country filtering and empty-selection tests keep the employer-first interaction consistent with its download and skills denominator. No standing-rule change needed.
- tags: jobs,us-scope,employer-selector

## 2026-11-02 -- For isolated Quarto checks, copy the current artifact_io.py data dependencies under outputs/site-reference, outputs/employer-page-review/data and outputs/us-employer-inventory/curated; data/ alone no longer supplies the pre-render bundle.
- Expected: Apply the blue-white-pink palette and render the existing website.
- Actual: Palette updated; shared render twice failed moving jobs.html. An isolated eight-page build succeeded after including current Parquet dependencies.
- Why: The repository changed concurrently, including conversion of build inputs to task-scoped Parquet. Shared build failure cause was not established. Read current dependencies before isolated verification; no standing rule changes proposed.
- tags: quarto,palette,concurrent-work

## 2026-11-02 -- For skill bubbles, key detail rendering by scope and skill index. Repeated mouseover events from child text must not replace the detail DOM; ignore hover while a source link inside skill-detail holds keyboard focus. Test both cases with the existing DOM fixture.
- Expected: Widen the site to 1100px and improve readability and hover accessibility.
- Actual: Widened body and CSS caps, increased spacing and type, added selection and control semantics, and verified repeated hover and focus protection. Isolated eight-page build and 282 local links passed; browser visual QA remains unavailable.
- Why: Bubbling mouseover events rebuilt the selected details unnecessarily. A selected-key guard preserves open source details. Shared Quarto output still encounters file-move failures, so verification used an isolated build. No standing-rule changes proposed.
- tags: accessibility,hover,quarto

## 2026-11-02 -- For the full employer inventory, reconcile 18,443 local and 4,549 Azure source rows separately from deduplicated US-relevant identities. Keep posted_at and created_at separate in compressed task-scoped Parquet; label created_at fallbacks as first-recorded proxies and include null posted_at rows in complete extracts.
- Expected: Expose complete employer coverage, independent filters and auditable dates in task-scoped data files.
- Actual: 22,992 raw rows retained; 253 US-relevant identities across 12 employers; 129 source posting dates and 124 collection proxies. Inventory, interactions and 282-link checks pass.
- Why: The earlier six-job example sample was a different population from the database extracts. Name matches, store overlap, geography and relevance reduce usable identities; missing posted dates require explicit provenance. No standing-rule change proposed.
- tags: parquet,inventory,dates,postgres,azure

## 2026-11-02 -- The 253-record commercial-only screen is not the full pharmaceutical data-careers population. Keep inclusion-rule counts in inventory-summary.parquet and generated methods; test clinical data, biostatistics, operations analysts and analytical duties with technical tools separately from commercial vendor signals. Use explicit UTF-8 for source reads and writes on Windows.
- Expected: Expand evidence-based US career coverage consistently across the website.
- Actual: 1,127 posting identities across 13 employers; 874 additions; eight pages rendered, 282 links and all inventory/filter checks passed.
- Why: Commercial title and vendor requirements excluded adjacent data careers. Broader documented rules preserve US evidence and deduplication. Encoding and concurrent card-layout changes were detected by checks and reconciled. No standing-rule changes proposed.
- tags: inventory,scope,parquet,encoding

## 2026-11-02 -- For website prose revisions, edit QMD pages, shared _includes, scripts/dashboard.js and scripts/build_site_data.py together. Generated findings and scenario text otherwise restore editorial instructions on the next build. Keep build commands in repository documentation rather than public methods prose.
- Expected: Use mechanism-first prose and remove internal commentary and instructions from public pages.
- Actual: Eight pages revised and rendered; 282 links and interaction checks passed; 1,127 postings across 13 employers preserved.
- Why: Public copy is distributed across page sources, HTML includes, browser templates and Python generators. Revised those sources and verified the local render. No standing-rule changes proposed.
- tags: writing,website,generated-copy

## 2026-11-02 -- Before rendering AD688 G0, inspect existing Quarto preview processes targeting this checkout. A running jobs.qmd preview competed for root HTML and _site files. Stop that preview before a release build; if Quarto openKv then reports disk I/O error, remove only this checkout .quarto cache and render again.
- Expected: Render all eight pages in the shared checkout and preserve recent changes in main.
- Actual: Clean temporary render passed; shared render passed after stopping the repository preview and clearing .quarto. Inventory, 282 local links and dashboard checks passed.
- Why: A Quarto preview targeting jobs.qmd was running while render moved shared HTML files. The subsequent cache error disappeared after removing .quarto. No standing-rule changes proposed.
- tags: quarto,build,cleanup

## 2026-11-03 -- Keep US inventory inclusion separate from analytics relevance: 9493 US identities are the default, 1127 are optional analytics matches, and 5071 missing posting dates retain yellow database-created-at pull proxies. Assert previous analytics IDs and dates survive broadening.
- Expected: Show every US job with optional analytics filtering and preserve date provenance.
- Actual: 9493 default records, 1127 analytics and 8366 other records; all 5071 pull tags verified through pagination; eight pages and 282 local links passed.
- Why: The previous relevance inclusion gate reduced the visible inventory. Moving relevance to a Boolean classification preserves the population and supports optional filtering. No standing-rule fix proposed.
- tags: inventory,scope,dates,filters

## 2026-11-03 -- Quarto compiles styles/theme.scss after Cosmo; preserve the partial import order because accessibility and compact-card rules override earlier shared responsive rules. Verify source-rule parity and that all eight HTML pages link the same compiled theme.
- Expected: Modularize the stylesheet without changing the existing design or interactions.
- Actual: 14 SCSS partials replace styles.css; exact source cascade parity, eight-page render, compiled component checks, 274 local links and dashboard interactions passed.
- Why: Later component refinements depended on cascade order. The migration retained that order and documented it in styles/README.md. No standing-rule fix needed; browser appearance was not visually checked.
- tags: scss,quarto,cascade

## 2026-11-03 -- Generate repeated page statistics from site-metrics.parquet and _variables.yml; test agreement with dashboard-data.js and rendered pages. Recalculate counts from curated records and BLS industry growth from employment endpoints; retain published occupational forecasts as source inputs.
- Expected: Replace repeated literal statistics with saved calculations shared across all pages.
- Actual: Eight pages rendered with shared variables; changed-input controls, snapshot and bundle parity, 275 links and existing interaction checks passed. One initial summary write failed; restored from the matching saved bundle before successful rebuilds.
- Why: Static homepage and methods figures duplicated values already present in evidence files. Central calculation and a Quarto post-render consistency check now detect disagreement. No standing-rule fix proposed.
- tags: metrics,quarto,consistency

## 2026-11-03 -- For native OJS pages, scope checkbox sizing separately from the global 44px input rule, set Inputs.table maxHeight explicitly when row padding changes, and limit nowrap to table-cell links. Verify reactive empty states by waiting for form.value, since empty Inputs.table renders a placeholder row. Use Playwright request interception for _site assets to exercise modules without starting a local server.
- Expected: Migrate Growth and Pay and Skills to native Quarto and OJS while preserving branding and evidence definitions.
- Actual: Both pages migrated; full eight-page render, 329 local links, data reconciliation, existing dashboard checks and Edge desktop/mobile interaction tests pass. Direct-file OJS initialization failed; intercepted local assets worked. Styling conflicts and asynchronous test assertions were corrected.
- Why: Existing global CSS affected Observable controls and table dimensions. Browser file loading did not initialize the Quarto module runtime, and OJS dependent outputs update asynchronously. No standing rule or skill change needed.
- tags: quarto,ojs,testing,responsive

## 2026-11-03 -- After an OJS migration, review README build instructions alongside the page sources: retain node scripts/test_ojs.cjs and scripts/test_ojs_browser.py checks, and remove claims that native module pages work fully offline through file URLs.
- Expected: Preserve every recent frontend and evidence update in a verified release.
- Actual: Eight pages, 329 links, inventory and metrics controls, dashboard tests and OJS desktop/mobile browser checks passed. Updated stale README instructions and removed temporary migration artifacts.
- Why: The frontend changed from bundled dashboard scripts to native OJS on two pages, while the README retained the previous direct-file and no-CDN claim. No standing-rule change proposed.
- tags: release,documentation,ojs

## 2026-11-06 -- Preserve the existing bubble and card designs when migrating their implementation to OJS. Quarto's html tagged helper does not attach interpolated event callbacks; attach listeners to returned DOM nodes. Update aria-pressed in a separate reactive cell so selecting a bubble does not rebuild it and lose focus.
- Expected: Restore the earlier pastel bubbles and occupation cards while retaining native Quarto/OJS controls and tables.
- Actual: Restored both designs; full render, data parity, existing dashboard tests, local links and desktop/mobile browser checks pass. An initial bubble click check caught unattached event handlers; explicit listeners resolved it.
- Why: The first migration changed the visual design beyond the user's intent. The restored OJS components reuse existing styling, while browser checks verify real event behavior and focus preservation. No standing-rule changes proposed.
- tags: ojs,design-preservation,events

## 2026-11-06 -- For Boston certificate market sizing, keep MassBio's 2026 mapped life-sciences members (760 Boston/Cambridge; 1437 MA), 2025 statewide workforce, and 2026 major-employer headcounts as distinct populations. The saved 15-name posting inventory covers only 8 of the 20 size-ranked companies; missing coverage is not zero demand. Require explicit MA geography and keep sponsorship scenarios separate from observed postings.
- Expected: Add employer market scale, company sizes and local employability evidence to the certificate website.
- Actual: Added a 20-employer table totaling 40521 MA staff; calculated 637 local postings, 112 analytics and 19 commercial-fit identities; nine pages rendered, 357 links and desktop/mobile calculator checks passed.
- Why: Membership, workforce and posting records have different scopes and dates. The inventory is selected and historical, with unresolved locations and missing posting dates. Mobile tables initially overflowed; page-scoped scrolling resolved it. No standing-rule changes proposed.
- tags: market-sizing,employers,geography

## 2026-11-06 -- For national pharma firm sizing, read the 2022 SUSB detailed-size download as cp1252 and select STATE=00, NAICS=3254. Exclude overlapping total/subtotal ENTRSIZE codes 01, 33 and 37 from bin sums. Enterprise-size bands use whole-enterprise employment while EMPL counts industry establishments; do not substitute establishments for firms or combine these counts with broader biopharma estimates.
- Expected: Extend Boston employer analytics nationally with firm sizes and US posting evidence.
- Actual: Added reconciled 2305 firms and six size bands, 15 employer tables, state evidence, sponsorship calculator and downloads. Ten pages, 366 links, data controls and desktop/mobile checks pass.
- Why: Census size tables contain overlapping subtotal rows and a different population from broader industry estimates. Initial UTF-8 decoding failed; cp1252 read the source correctly. No standing-rule changes proposed.
- tags: market-sizing,census,aggregation

## 2026-11-06 -- Broad local pharma scans require explicit QA after the first aggregate: pharmacy data-entry roles can pass generic data-title rules, and Hyderabad Ts, Indiana can require a recruiting-URL conflict override. Keep all original rows and separate strict analytics-title candidates from broader domain matches. Pin pending enrichment by IDs and extract hash; offline screening does not clear production statuses.
- Expected: Broaden employer coverage and identify early-career training prospects from local PostgreSQL.
- Actual: Scanned 10,654,778 rows, processed 357,230 candidates, reconciled 124,101 US candidate identities and 5,822 analytics-title matches across 1,254 labels. QA corrected role and geography false positives. Eleven pages rendered and 485 links passed. Prepared and plan-tested a runner for 279,358 exact pending IDs; no database writes or production execution.
- Why: Company counts, industry keyword matches, valid geography, career eligibility and completed enrichment are different populations. Preserve distinctions and inspect example evidence before presenting totals. Existing script-only execution rule retained; no standing-rule fix proposed.
- tags: local-pg,scope,early-career,geography,enrichment

## 2026-11-06 -- Serialize Quarto Publish runs with the fixed quarto-gh-pages concurrency group and cancel-in-progress false. Successive main pushes otherwise race on the shared gh-pages ref even when both renders pass.
- Expected: Both consecutive release pushes publish successfully.
- Actual: The first publisher succeeded; the receipt-commit publisher failed because gh-pages advanced from 92e4dc7 to 6f3d53c. Added workflow concurrency and validated the YAML.
- Why: The publish workflow allowed concurrent writers to the same gh-pages branch. The final receipt push overlapped the preceding release publish.
- tags: github-actions,quarto,concurrency,fix-applied

## 2026-11-06 -- For visual market pages, keep complementary map detail in a div with role=complementary because Quarto moves literal aside elements into margin columns. Inside raw details disclosures, use bold evidence subheads rather than same-level section headings, which can close the disclosure. Run snapshot-hash checks only after all pre-render builders finish.
- Expected: Replace table-led employer pages with maps/charts and Azure-backed county context.
- Actual: US/Boston visual explorers added; Azure read-only export produced 2024 county estimates, exact FIPS joins and quality flags. Eleven pages rendered, 495 links and desktop/mobile map/chart/calculator checks passed; concurrent Parquet migration preserved.
- Why: Quarto interprets aside and section headings structurally. Early checks also overlapped changing generated inputs and a separate storage migration. Corrected layout, rebuilt against final Parquet paths and reverified. No standing-rule changes proposed.
- tags: quarto,visuals,county,concurrent-work

## 2026-11-06 -- Quarto resolves nested includes before pre-render builders can create missing files. Bootstrap a newly generated include once before the first render, then retain the generated include alongside its builder. Verify Parquet migration through exact snapshot readback, download links and source-to-site parity.
- Expected: Move analytical datasets to Parquet and display broad training counts consistently.
- Actual: Migrated market snapshots and downloads; eleven pages rendered, all market checks and 495 local links passed. First render needed the new overview include generated explicitly.
- Why: The include did not yet exist when Quarto resolved page inputs. Generated it before rendering and verified homepage counts against the saved Parquet summary. No standing-rule changes proposed.
- tags: quarto,parquet,build-order

## 2026-11-06 -- When extending README build commands, edit only the fenced build block. A global replacement of python scripts/test_site_metrics.py also expanded its inline prose reference into a malformed multiline code span; inspect every replacement occurrence.
- Expected: Extend build instructions while preserving explanatory prose.
- Actual: Found and corrected the malformed metrics paragraph; added the visual-market checks only inside the build code block.
- Why: The earlier release used a global string replacement for a command present in both a code block and an inline reference. No standing-rule change required.
- tags: documentation,release,editing

## 2026-11-07 -- If snapshot_io.py raises WinError 32 during atomic Parquet replacement, treat the build as failed, inspect competing processes and rerun the full render before checking provenance. After success, remove only the identified orphan UUID .tmp file; do not commit partial output.
- Expected: Build and verify all updated pages before committing.
- Actual: First render stopped on a locked temporary employers.parquet file. No competing build process was found; a complete retry and all data, link and browser checks passed.
- Why: Windows reported an open-file lock; its owner was not established. The atomic writer preserved the prior target, and the retry regenerated dependent outputs. No code or standing-rule change proposed.
- tags: windows,parquet,release
- Follow-up: Quarto resource copying had also placed the failed-render temp file under _site. Check both source and rendered resource trees; verify_site.py now rejects any .tmp site artifact. Corrected release 413a002 passed publication and Pages deployment.

## 2026-11-07 -- Preserve the homepage circular blue-and-pink graphic: the user explicitly values it. In Quarto, canonicalizeTitlePostprocessor can move the first H1 into a generated title header; a semantic hero header with quarto-title-block preserves the authored position. Verify the rendered hero, not just source markup.
- Expected: Review and simplify generic presentation while preserving user-valued design and factual evidence.
- Actual: Completed independent design/browser reviews and live SEO checks; restored the circular hero after user correction; fixed H1 positioning and verified responsive screenshots and 457 links.
- Why: A generic anti-template heuristic overrode an unexpressed visual preference; the user clarified it. Quarto also relocates eligible H1 elements during HTML postprocessing. Preference and rendering behavior are now recorded; no standing-rule change proposed.
- tags: design-preference,quarto,visual-verification
