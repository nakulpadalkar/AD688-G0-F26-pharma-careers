"""Check saved calculations, changed-input behavior and rendered consistency."""
import json
import re
from copy import deepcopy
from pathlib import Path
from artifact_io import read_data, TASK
from site_metrics import derive_inventory, derive_metrics

ROOT = Path(__file__).resolve().parents[1]
bundle = json.loads((TASK/'web/dashboard-data.js').read_text(encoding='utf-8').removeprefix('window.PHARMA_DATA = ').strip().removesuffix(';').replace('<\\/', '</'))
raw = read_data('all-employer-records')
summary = derive_inventory(bundle['jobs'], raw, bundle['inventory'])
assert summary == bundle['inventory'] == read_data('inventory-summary')
courses = len(re.findall(r'^\| \d+\.', (ROOT/'about.qmd').read_text(encoding='utf-8'), re.M))
metrics = derive_metrics(bundle, courses)
assert metrics == read_data('site-metrics') == bundle['metrics']
assert json.loads((ROOT/'_variables.yml').read_text(encoding='utf-8')) == metrics['values']
# Alter evidence, not expectations, to prove counts and forecasts are computed.
removed = bundle['jobs'][0]
changed = derive_inventory(bundle['jobs'][1:], raw[:-1], summary)
assert changed['job_count'] == summary['job_count'] - 1
assert changed['analytics_relevant_jobs'] == summary['analytics_relevant_jobs'] - bool(removed['analytics_relevant'])
assert changed['undated_jobs'] == summary['undated_jobs'] - (not removed['posted_on'])
assert sum(changed['source_counts'].values()) == len(raw) - 1
assert sum(c['jobs'] for c in changed['companies']) == len(bundle['jobs']) - 1
altered = deepcopy(bundle)
start, end = map(int, re.findall(r'\d{4}', altered['benchmarks']['projection_period']))
industry = altered['benchmarks']['industry']
industry[f'employment_{end}'] = industry[f'employment_{start}'] * 2
new = derive_metrics(altered, courses + 1)
assert new['industry']['growth_percent'] == 100
assert new['industry']['annual_growth_percent'] > metrics['industry']['annual_growth_percent']
assert new['values']['course_count'] == str(courses + 1)
assert new['source_sha256'] != metrics['source_sha256']
# Every variable used in a page must be defined and resolved by Quarto.
for source in [*ROOT.glob('*.qmd'), * (ROOT/'_includes').glob('*.html')]:
    for key in re.findall(r'\{\{< var (\w+) >\}\}', source.read_text(encoding='utf-8')):
        assert key in metrics['values'], (source, key)
for name in ['index','jobs','geography','outlook','skills','work','about','eda_pharma']:
    html = (ROOT/'_site'/f'{name}.html').read_text(encoding='utf-8')
    assert '{{< var' not in html and 'var not found' not in html.lower(), name
for name, keys in {
    'index': ['meteor_commercial_candidates','industry_growth','job_count','inventory_date'],
    'outlook': ['industry_base','industry_projected','industry_growth','industry_annual_growth'],
    'eda_pharma': ['meteor_database_records','meteor_commercial_candidates','mapped_records','local_records','azure_records','raw_records','industry_base','industry_projected'],
}.items():
    html = (ROOT/'_site'/f'{name}.html').read_text(encoding='utf-8')
    for key in keys:
        assert metrics['values'][key] in html, (name, key)
print('METRICS_OK: recalculated counts, changed-input controls, saved snapshot/variables/bundle parity and rendered values')
