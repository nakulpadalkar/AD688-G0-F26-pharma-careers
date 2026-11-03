"""Export employer-scoped source evidence privately, with read-only DB sessions."""
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from dotenv import dotenv_values
import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq
import hashlib
from artifact_io import TASK
from audit_company_coverage import COMPANIES
ROOT=Path(__file__).resolve().parents[1]
COMPANIES.update({'Neurocrine Biosciences':r'\mneurocrine\M','Otsuka':r'\motsuka\M','Teva':r'\mteva\M','Vertex Pharmaceuticals':r'\mvertex\M','IQVIA':r'\miqvia\M'})
FIELDS=['id','source','external_id','title','company_name','location_text','city','state','countryiso','posted_at','apply_url','is_active','is_duplicate','description','html_description_text','alive','alive_checked_at','alive_valid_until','requirements_summary','responsibilities_summary','technical_tools_summary','created_at','html_fetched_at']
def main():
 p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--alias',choices=['local','azure'],required=True);a=p.parse_args()
 env=dotenv_values(a.env_file);bridge=bool(env.get('LOCAL_DB_HOST'));prefix=('LOCAL_DB_' if bridge else 'DB_') if a.alias=='local' else ('DB_' if bridge else 'AZURE_DB_')
 host=env.get(prefix+'HOST','').lower().rstrip('.')
 assert (host in ('localhost','127.0.0.1','::1')) if a.alias=='local' else host.endswith('.postgres.database.azure.com')
 cfg={k:env.get(prefix+v) for k,v in [('host','HOST'),('port','PORT'),('dbname','NAME'),('user','USER'),('password','PASSWORD')]}
 conn=psycopg2.connect(**cfg,connect_timeout=15,sslmode='require' if a.alias=='azure' else 'prefer',application_name='pharma_inventory_readonly',options='-c default_transaction_read_only=on -c statement_timeout=300000 -c lock_timeout=3000 -c timezone=UTC')
 conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
 out=TASK/'raw';out.mkdir(parents=True,exist_ok=True);(TASK/'manifests').mkdir(exist_ok=True)
 try:
  with conn.cursor() as q:
   q.execute("select current_setting('transaction_read_only'),current_setting('transaction_isolation')");transaction=q.fetchone();assert transaction[0]=='on'
   q.execute("select column_name from information_schema.columns where table_schema='public' and table_name='met_career_match_jobposting'");available={r[0] for r in q.fetchall()}
   fields=[f for f in FIELDS if f in available]
   assert {'id','source','external_id','company_name','title','description','location_text','countryiso','apply_url'}<=set(fields)
   query='SELECT '+','.join(fields)+' FROM met_career_match_jobposting WHERE company_name ~* %s ORDER BY id'
   q.execute(query,('|'.join(COMPANIES.values()),))
   rows=[dict(zip(fields,r)) for r in q.fetchall()]
  for row in rows:
   row['posted_at_raw']=str(row['posted_at']) if row.get('posted_at') else None
   row['date_basis']='source_reported_posted_at' if row.get('posted_at') else 'database_created_at_proxy' if row.get('created_at') else 'unknown'
   row['display_date']=row.get('posted_at') or row.get('created_at')
  payload={'alias':a.alias,'checked_at_utc':datetime.now(timezone.utc).isoformat(),'transaction':transaction,'query':query,'company_patterns':COMPANIES,'date_window':'All available posting dates; no row limit','missing_columns':sorted(set(FIELDS)-available),'rows':rows}
  payload.pop('rows');path=out/f'{a.alias}.parquet';pq.write_table(pa.Table.from_pylist(rows),path,compression='zstd');assert pq.read_metadata(path).num_rows==len(rows);payload['row_count']=len(rows);payload['parquet_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(TASK/f'manifests/{a.alias}.json').write_text(json.dumps(payload,default=str,indent=2),encoding='utf-8')
  print(json.dumps({'alias':a.alias,'rows':len(rows),'missing_columns':payload['missing_columns'],'transaction':transaction}),flush=True)
 finally:conn.rollback();conn.close()
if __name__=='__main__':main()
