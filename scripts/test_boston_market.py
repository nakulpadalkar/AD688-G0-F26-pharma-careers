from snapshot_io import read_snapshot, write_snapshot
"""Geography controls, population reconciliation and changed-input checks."""
import hashlib
import json
from copy import deepcopy
from build_boston_market import OUT, ROOT, compute, region, commercial
from artifact_io import read_data

for location, expected in [
    ('Boston, MA', 'Boston / Cambridge'), ('Cambridge, Massachusetts', 'Boston / Cambridge'),
    ('Waltham, MA, us', 'Outreach suburbs'), ('Worcester, Massachusetts', 'Other Massachusetts'),
    ('Burlington, VT, us', 'outside_or_unresolved'), ('Lexington, Kentucky', 'outside_or_unresolved'),
    ('Cambridge ()', 'outside_or_unresolved'), ('Remote', 'outside_or_unresolved'),
    ('Boston, Massachusetts, New York', 'outside_or_unresolved'),
    ('Ma Cambridge Kendall Square 500', 'outside_or_unresolved')]:
    assert region({'location': location, 'country': 'US'}) == expected, location
assert region({'location': 'Boston, MA', 'country': 'CA'}) == 'outside_or_unresolved'
assert commercial({'analytics_relevant': True, 'relevance_basis': 'commercial_analytics_title'})
assert not commercial({'analytics_relevant': True, 'relevance_basis': 'pharma_data_science_or_informatics_title'})
jobs = read_data('database-jobs.json')
employers = read_snapshot((OUT/'data/employers.parquet'))
saved = read_snapshot((OUT/'web/market-summary.parquet'))
fresh = compute(jobs, employers)
assert all(saved[k] == v for k, v in fresh.items())
assert len({r['id'] for r in jobs}) == len(jobs)
assert sum(fresh['geography_counts'].values()) == len(jobs)
assert fresh['core']['postings'] <= fresh['local']['postings'] <= fresh['ma']['postings'] <= fresh['us']['postings']
for key in ['core', 'local', 'ma', 'us']:
    d = fresh[key]
    assert d['commercial'] <= d['analytics'] <= d['postings']
assert len(employers) == len({e['company'] for e in employers}) == 20
assert sum(e['ma_employees'] for e in employers) == 40521
for path, expected in saved['source_sha256'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected
target = next(r for r in jobs if region(r) == 'Boston / Cambridge' and commercial(r))
changed = compute([r for r in jobs if r['id'] != target['id']], employers)
assert changed['local']['postings'] == fresh['local']['postings'] - 1
assert changed['local']['commercial'] == fresh['local']['commercial'] - 1
altered = deepcopy(employers); altered[0]['ma_employees'] += 10
assert compute(jobs, altered)['shortlist_employees'] == fresh['shortlist_employees'] + 10
print('BOSTON_MARKET_OK: geography controls, populations, source hashes and changed-input controls')
