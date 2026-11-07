from snapshot_io import read_snapshot, write_snapshot
"""Source join, null/zero, scale and provenance checks for visual market data."""
import hashlib
import json
from build_market_visuals import ROOT,OUT,value,TERRITORIES

source=read_snapshot((OUT/'data/urban-counties.parquet'))
payload=json.loads((OUT/'web/visual-data.js').read_text(encoding='utf-8').removeprefix('window.MARKET_VISUALS = ').strip().removesuffix(';').replace('<\\/','</'))
rows={r['geoid']:r for r in source['rows']}
counties=payload['counties'];meta=payload['county_meta']
assert source['transaction_read_only'] is True and source['database_alias']=='azure'
assert meta['year']==max(y for y,n in source['coverage_by_year'] if n)
assert len({r['geoid'] for r in counties})==len(counties)
for r in counties:
    assert len(r['geoid'])==5 and r['geoid'][:2] not in TERRITORIES
    assert (r['value'],r['status'])==value(rows.get(r['geoid'],{}))
    assert r['path'].startswith('M') and r['bbox'][0]<=r['bbox'][2]
    if r['value'] is not None:assert 0<=r['value']<=100
assert meta['mapped']==sum(r['value'] is not None for r in counties)
assert sum(meta['statuses'].values())==len(counties)
assert value({'share_employed':'0','in_universe':True})==(0,'available')
assert value({'share_employed':None})==(None,'missing')
assert value({'share_employed':'.8','in_universe':False})==(None,'outside_universe')
assert value({'share_employed':'.8','share_employed_quality':'Weak'})==(80,'low_quality')
assert value({'share_employed':'80'})==(None,'missing')
for label,path in [('us','outputs/us-market/web/summary.parquet'),('boston','outputs/boston-market/web/market-summary.parquet')]:
    assert payload[label]==read_snapshot(ROOT/path)
receipt=read_snapshot((OUT/'web/provenance.parquet'))
for path,digest in receipt['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
for page in ['us-market','boston-market']:
    text=(ROOT/(page+'.qmd')).read_text(encoding='utf-8')
    assert '_includes/market-visuals.html' in text and '<details class="market-evidence">' in text
print('MARKET_VISUALS_OK: Azure read-only provenance, exact FIPS, null/zero/quality and snapshot parity')
