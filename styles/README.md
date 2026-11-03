# Site styles

Quarto compiles `theme.scss` after the Cosmo theme. Edit the SCSS partials here, then run `quarto render`. No separate Sass install or CSS build command is needed.

- `_tokens.scss`: shared colors exposed as CSS custom properties.
- `_base.scss`: typography, navbar and main content width.
- `_home.scss`: hero, source strip and metrics.
- `_shared.scss`: panels, headings and common labels.
- `_geography.scss`: map, legend, state details and tables.
- `_outlook.scss`: benchmark and industry cards.
- `_jobs.scss`: filters and base job layout.
- `_skills-work.scss`: shared skills, work scenarios and certificate pathway.
- `_footer-utilities.scss`: footer, focus states and utility elements.
- `_responsive.scss`: shared breakpoints, reduced motion and print.
- `_navigation.scss`: page directory and focused-page layout.
- `_skill-bubbles.scss`: interactive skill bubbles and metadata panel.
- `_accessibility.scss`: readable sizing and persistent selection overrides.
- `_native-analytics.scss`: native OJS controls, charts and sortable tables for Growth & Pay and Skills.
- `_job-cards.scss`: compact three-column cards, qualification tags and yellow pulled dates.

Imports intentionally preserve the original cascade: later component refinements follow shared responsive rules. Keep that ordering when editing overlapping selectors. Runtime chart dimensions and bubble sizes remain data-driven CSS values in the dashboard; their appearance lives here.
