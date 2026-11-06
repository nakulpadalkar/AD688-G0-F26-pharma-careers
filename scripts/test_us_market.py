"""Check independent totals, nonoverlapping Census bands and changed-input behavior."""
import json
import hashlib
from copy import deepcopy
from build_us_market import OUT, ROOT, BANDS, compute, state
from artifact_io import read_data
from build_boston_market import commercial

census=json.loads((OUT/'data/census-3254.json').read_text(encoding='utf-8'))
jobs=read_data('database-jobs.json')
actual=compute(jobs,census)
saved=json.loads((OUT/'web/summary.json').read_text(encoding='utf-8'))
assert all(saved[k]==v for k,v in actual.items())
codes=[c for _,cs in BANDS for c in cs]
assert len(codes)==len(set(codes)) and not {'01','33','37'}.intersection(codes)
for key in ['FIRM','ESTB','EMPL']:
    assert sum(r[key] for r in actual['bands'])==actual['census_total'][key]
assert actual['census_total']['FIRM']==2305
assert len({r['id'] for r in jobs})==len(jobs)
for key in ['postings','analytics','commercial','missing_posted_date']:
    assert sum(r[key] for r in actual['employers'])==actual['inventory'][key]
    assert sum(r[key] for r in actual['states'])==actual['inventory'][key]
for location,expected in [('Boston, MA','MA'),('Cambridge ()','Unallocated'),('Remote','Unallocated'),('New York, New York','NY'),('Boston, MA; Newark, NJ','Unallocated')]:
    assert state({'location':location,'country':'US'})==expected
target=next(r for r in jobs if commercial(r))
changed=compute([r for r in jobs if r['id']!=target['id']],census)
assert changed['inventory']['commercial']==actual['inventory']['commercial']-1
altered=deepcopy(census)
next(r for r in altered['rows'] if r['ENTRSIZE']=='02')['FIRM']='780'
assert compute(jobs,altered)['bands'][0]['FIRM']==actual['bands'][0]['FIRM']+1
for path,digest in saved['input_sha256'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
print('US_MARKET_OK: Census band reconciliation, US/employer/state parity, geography and changed inputs')
