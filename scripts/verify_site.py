"""Focused evidence and generated-asset checks; no network or server."""
import hashlib, json, re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_evidence import locate
from artifact_io import read_data,artifact_path,TASK
from snapshot_io import read_snapshot
from build_site_data import map_svg, employer_analysis
ROOT=Path(__file__).resolve().parents[1]
def read(name):return read_data(name)
d=read('meteor.json'); n=d['counts']['commercial_candidates']
assert n==1353
assert sum(m['records'] for m in d['monthly'])==n
assert len(d['monthly'])==21 and len({m['month'] for m in d['monthly']})==21
assert sum(d['geography']['buckets'].values())==n
assert sum(s['records'] for s in d['geography']['states'])==d['geography']['mapped_records']==654
assert len(d['geography']['states'])==51
for s in d['geography']['states']:assert 0<=s['distinct_employer_text_hashes']<=s['records']
controls=[('Boston, MA','',('mapped_state','MA')),('Washington, DC','',('mapped_state','DC')),('Remote','',('remote_unallocated',None)),('Hyderabad, Indiana','',('location_conflict',None)),('Toronto, Ontario','',('explicit_non_us',None)),('Boston, MA','CA',('explicit_non_us',None)),('California; New York','',('ambiguous_or_multi_location',None)),('United States','',('us_unallocated',None)),('','',('unknown',None)),('Poland, Ohio','',('mapped_state','OH')),('IN OFFICE','',('unknown',None))]
for location,country,expected in controls:assert locate({'location_text':location,'countryiso':country})==expected,(location,expected)
assert len(read('reviewed-examples.json'))==13
jobs=read('current-jobs.json')
assert len({j['company'] for j in jobs})>=8
assert len({(j['company'],j['id']) for j in jobs})==len(jobs)
for j in jobs:
    assert j['checked_on']=='2026-11-02' and j['url'].startswith('https://')
    assert j['required'] and j['source_access'] and j['country']
    assert (j['salary_min'] is None and j['salary_max'] is None) or 0<j['salary_min']<j['salary_max']
    assert set(j['skills'])==set(j['skill_evidence']) and len(j['skills'])==len(set(j['skills']))
    assert all(j['skill_evidence'].values())
    if j['availability']=='application_observed':assert j['source_access']=='Readable employer page'
assert read('employer-analysis.json')==employer_analysis(read('database-jobs.json'))
b=read('benchmarks.json');assert b['wage_year']==2025
assert b['industry']['employment_2035']>b['industry']['employment_2025']
for s in d['skills']:assert 0<=s['records']<=s['denominator']==n
bundle=(TASK/'web/dashboard-data.js').read_text(encoding='utf-8')
payload=json.loads(bundle.removeprefix('window.PHARMA_DATA = ').strip().removesuffix(';').replace('<\\/','</'))
for key,name in [('meteor','meteor.json'),('current','current-jobs.json'),('historical','reviewed-examples.json'),('benchmarks','benchmarks.json'),('employer_analysis','employer-analysis.json'),('jobs','database-jobs.json'),('inventory','inventory-summary.json'),('metrics','site-metrics')]:assert payload[key]==read(name),f'Stale bundle: {key}'
assert payload['map']==map_svg(read('usa_110m.json'))
assert len(re.findall('data-state=',payload['map']))==51
assert not re.search(r'NaN|Infinity',payload['map'])
assert set(re.findall(r'data-state="([A-Z]{2})"',payload['map']))=={s['code'] for s in d['geography']['states']}
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for k in ['src','href']:
            if k in a:self.links.append(a[k])
site=ROOT/'_site'; checked=0
for page in ['index.html','geography.html','outlook.html','jobs.html','skills.html','work.html','eda_pharma.html','about.html','boston-market.html','training-market.html','us-market.html']:
    file=site/page;p=Links();p.feed(file.read_text(encoding='utf-8'));assert len(p.ids)==len(set(p.ids)),f'Duplicate id: {page}'
    for link in p.links:
        u=urlsplit(link)
        assert Path(u.path).suffix.lower() not in {'.csv','.xlsx','.xls'}, f'Non-Parquet download: {page}: {link}'
        if u.scheme or link.startswith('//'):continue
        target=(file.parent/unquote(u.path)).resolve() if u.path else file
        assert target.exists(),f'Broken local link: {page}: {link}'
        if u.fragment and target.suffix=='.html':
            q=Links();q.feed(target.read_text(encoding='utf-8'));assert unquote(u.fragment) in q.ids,f'Broken anchor {link}'
        checked+=1
resources=['outputs/us-employer-inventory/web/dashboard-data.js','scripts/dashboard.js']+[artifact_path(name).relative_to(ROOT).as_posix() for name in ['meteor','current-jobs','benchmarks','employer-analysis','us-jobs','database-jobs','inventory-summary','all-employer-records','site-metrics']]
resources += ['outputs/training-market/web/'+name for name in ['summary.parquet','employer-prospects.parquet','analytics-postings.parquet']]
for market in ['boston-market','us-market','market-visuals']:
    resources += [p.relative_to(ROOT).as_posix() for p in (ROOT/'outputs'/market/'web').glob('*.parquet')]
for rel in resources:
    assert (ROOT/rel).read_bytes()==(site/rel).read_bytes(),f'Stale published resource: {rel}'
# Every page must load Quarto's compiled theme, including the custom SCSS rules.
themes=set()
for page in ['index','geography','outlook','jobs','skills','work','eda_pharma','about','boston-market','training-market','us-market']:
 html=(site/(page+'.html')).read_text(encoding='utf-8')
 assert 'href="styles.css"' not in html
 match=re.search(r'<link href="([^"]+)"[^>]+id="quarto-bootstrap"',html)
 assert match, f'Missing compiled theme: {page}'
 themes.add(match.group(1))
assert len(themes)==1
compiled=(site/themes.pop()).read_text(encoding='utf-8')
for selector in ['.source-strip','.job-pull-date','.skill-bubble','.job-grid','prefers-reduced-motion']:
 assert selector in compiled, f'Missing SCSS component: {selector}'
assert not (site/'outputs/us-employer-inventory/raw').exists()
assert not (site/'outputs/training-market/raw').exists()
assert not (site/'outputs/training-market/processed').exists()
for forbidden in ['candidates.json','audit.json','.env','build_evidence.py','company-coverage-local.json','company-coverage-azure.json','audit_company_coverage.py','inventory-local.json','inventory-azure.json','geography-review.json','fetch_inventory.py']:
    assert not list(site.rglob(forbidden)),f'Unexpected source in site: {forbidden}'
assert 'Tools mentioned in METEOR' not in (site/'skills.html').read_text(encoding='utf-8')
assert 'home-inventory-metric' in (site/'index.html').read_text(encoding='utf-8')
for rel in ['scripts/dashboard.js','jobs.qmd','skills.qmd']:
    assert not any(bad in (ROOT/rel).read_text(encoding='utf-8') for bad in ['Ã','â€','Â·','â†','�']),f'Encoding artifact: {rel}'

assert read('us-jobs.json')==read('database-jobs.json')
assert 'job-country' not in (site/'jobs.html').read_text(encoding='utf-8')
print(f'EVIDENCE_OK: 11 geography controls, count reconciliation, 51 map states, fresh bundles, {checked} local links and anchors')

assert not [p for p in site.rglob('*') if p.suffix.lower() in {'.csv','.xlsx','.xls'}]
summary=read_snapshot(ROOT/'outputs/training-market/web/summary.parquet')
career=summary['us']['career']
early=career.get('Explicit early-career title',0)+career.get('0–3-year experience signal; review required',0)
index=(site/'index.html').read_text(encoding='utf-8')
for count in [summary['us']['analytics'],summary['analytics_employer_labels'],early]:
    assert f'<strong>{count:,}</strong>' in index, f'Missing homepage count: {count}'
print('PARQUET_SITE_OK: download formats, snapshot parity and calculated homepage counts')
