"""Pin only this extract's pending IDs; never change database statuses."""
import hashlib
import json
from pathlib import Path
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/training-market'
receipt=json.loads((OUT/'receipt.json').read_text())
source=OUT/'raw/local-candidates.parquet'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==receipt['raw_sha256']
ids=[]
for batch in pq.ParquetFile(source).iter_batches(columns=['id','enrichment_status']):
    ids.extend(int(r['id']) for r in batch.to_pylist() if r['enrichment_status']=='pending')
ids=sorted(set(ids))
assert len(ids)==receipt['candidate_enrichment_status']['pending']
folder=OUT/'enrichment';folder.mkdir(exist_ok=True)
payload=json.dumps(ids,separators=(',',':'))+'\n'
target=folder/'pending-ids.json'
if target.exists():assert target.read_text()==payload,'Existing pinned cohort differs; use a new output root'
else:target.write_text(payload,encoding='utf-8')
manifest={'scope':'Only IDs pending in this exact broad local candidate extract; includes non-US and unresolved candidates. No global backlog selection or reset.',
          'candidate_records':receipt['candidate_records'],'pending_ids':len(ids),'raw_sha256':receipt['raw_sha256'],
          'ids_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'extracted_at':receipt['completed_at_utc'],
          'production_executed':False,'note':'Offline classifications do not clear database enrichment_status. Finalization must verify persisted stage evidence.'}
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'PINNED_PENDING_IDS':len(ids),'ids_sha256':manifest['ids_sha256'],'database_writes':0}))
