"""Read collection timestamps for the pinned extracts and migrate them to Parquet."""
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import pyarrow as pa
import pyarrow.parquet as pq
import psycopg2
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/us-employer-inventory'
def main():
 p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--alias',choices=['local','azure'],required=True);a=p.parse_args()
 original=ROOT/f'docs/private/inventory-{a.alias}.json';payload=json.loads(original.read_text(encoding='utf-8'));rows=payload.pop('rows')
 env=dotenv_values(a.env_file);bridge=bool(env.get('LOCAL_DB_HOST'));prefix=('LOCAL_DB_' if bridge else 'DB_') if a.alias=='local' else ('DB_' if bridge else 'AZURE_DB_');host=env.get(prefix+'HOST','').lower().rstrip('.')
 assert (host in ('localhost','127.0.0.1','::1')) if a.alias=='local' else host.endswith('.postgres.database.azure.com')
 cfg={k:env.get(prefix+v) for k,v in [('host','HOST'),('port','PORT'),('dbname','NAME'),('user','USER'),('password','PASSWORD')]}
 conn=psycopg2.connect(**cfg,connect_timeout=15,sslmode='require' if a.alias=='azure' else 'prefer',application_name='pharma_dates_readonly',options='-c default_transaction_read_only=on -c statement_timeout=60000 -c lock_timeout=3000 -c timezone=UTC');conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
 dates={}
 try:
  with conn.cursor() as q:
   q.execute("select current_setting('transaction_read_only')");assert q.fetchone()[0]=='on'
   ids=[r['id'] for r in rows]
   for start in range(0,len(ids),1000):
    q.execute('SELECT id,created_at,html_fetched_at FROM met_career_match_jobposting WHERE id = ANY(%s)',(ids[start:start+1000],))
    dates.update({r[0]:r[1:] for r in q.fetchall()})
 finally:conn.rollback();conn.close()
 for r in rows:
  r['posted_at_raw']=r.get('posted_at')
  for key in ['posted_at','alive_checked_at','alive_valid_until']:
   if r.get(key):r[key]=datetime.fromisoformat(r[key]).astimezone(timezone.utc)
  r['created_at'],r['html_fetched_at']=dates.get(r['id'],(None,None))
  r['date_basis']='source_reported_posted_at' if r.get('posted_at') else 'database_created_at_proxy' if r.get('created_at') else 'unknown'
  r['display_date']=r.get('posted_at') or r.get('created_at')
 (OUT/'raw').mkdir(parents=True,exist_ok=True);(OUT/'manifests').mkdir(exist_ok=True)
 path=OUT/f'raw/{a.alias}.parquet';pq.write_table(pa.Table.from_pylist(rows),path,compression='zstd')
 back=pq.read_table(path).to_pylist();assert len(back)==len(rows);assert {r['id'] for r in back}=={r['id'] for r in rows}
 assert all(x['description']==y['description'] and x['external_id']==y['external_id'] for x,y in zip(rows,back))
 payload.update(row_count=len(rows),timestamp_lookup_at_utc=datetime.now(timezone.utc).isoformat(),timestamp_rows_found=len(dates),source_json_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),parquet_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),compression='zstd',date_note='created_at is database creation/collection time, not actual posting time; no fabricated date imputation.')
 (OUT/f'manifests/{a.alias}.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
 print(json.dumps({'alias':a.alias,'rows':len(rows),'source_dates':sum(bool(r.get('posted_at')) for r in rows),'proxy_dates':sum(r['date_basis']=='database_created_at_proxy' for r in rows),'unknown_dates':sum(r['date_basis']=='unknown' for r in rows),'parquet_bytes':path.stat().st_size,'json_bytes':original.stat().st_size}))
if __name__=='__main__':main()
