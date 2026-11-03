"""Bounded, read-only company coverage audit. Never exports connection details."""
import argparse, json, re
from pathlib import Path
from datetime import datetime, timezone
from dotenv import dotenv_values
import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq
from artifact_io import REVIEW

ROOT=Path(__file__).resolve().parents[1]
COMPANIES={'AbbVie':r'\mabbvie\M','Iovance Biotherapeutics':r'\miovance\M','Amgen':r'\mamgen\M','AstraZeneca':r'\mastra\s?zeneca\M','Takeda':r'\mtakeda\M','Gilead Sciences':r'\mgilead\M','Regeneron':r'\mregeneron\M','Pfizer':r'\mpfizer\M','Novartis':r'\mnovartis\M','Sanofi':r'\msanofi\M'}
TITLE=r'analyst|analytics|data scien|data steward|data govern|master data|business intelligence|forecast|insights'

def audit(alias, env):
    bridge=bool(env.get('LOCAL_DB_HOST'))
    prefix=('LOCAL_DB_' if bridge else 'DB_') if alias=='local' else ('DB_' if bridge else 'AZURE_DB_')
    host=env.get(prefix+'HOST','').lower().rstrip('.')
    assert (host in ('localhost','127.0.0.1','::1')) if alias=='local' else host.endswith('.postgres.database.azure.com'), 'Unexpected database target'
    cfg={k:env.get(prefix+v) for k,v in [('host','HOST'),('port','PORT'),('dbname','NAME'),('user','USER'),('password','PASSWORD')]}
    conn=psycopg2.connect(**cfg,connect_timeout=15,sslmode='require' if alias=='azure' else 'prefer',application_name='pharma_company_coverage_readonly',options='-c default_transaction_read_only=on -c statement_timeout=180000 -c lock_timeout=3000 -c timezone=UTC')
    conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
    result={'alias':alias,'checked_at_utc':datetime.now(timezone.utc).isoformat(),'window':'2025-01-01 inclusive to 2026-11-03 exclusive UTC','companies':[]}
    try:
        with conn.cursor() as q:
            q.execute("select current_setting('transaction_read_only')")
            assert q.fetchone()[0]=='on'
            result['transaction_read_only']=True
            result['timezone']='UTC'
            result['company_patterns']=COMPANIES
            result['analytics_title_regex']=TITLE
            q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name ILIKE '%company%' OR table_name='met_career_match_jobposting') ORDER BY 1")
            result['candidate_tables']=[r[0] for r in q.fetchall()]
            q.execute("SELECT company_name,count(*),count(*) FILTER (WHERE title ~* %s),min(posted_at)::text,max(posted_at)::text FROM met_career_match_jobposting WHERE posted_at >= '2025-01-01' AND posted_at < '2026-11-03' AND company_name ~* %s GROUP BY company_name ORDER BY 1",(TITLE,'|'.join(COMPANIES.values())))
            rows=q.fetchall()
            for company,pattern in COMPANIES.items():
                py_pattern=pattern.replace(r'\m',r'\b').replace(r'\M',r'\b')
                matches=[r for r in rows if re.search(py_pattern,r[0],re.I)]
                result['companies'].append({'company':company,'posting_records':sum(r[1] for r in matches),'analytics_title_records':sum(r[2] for r in matches),'employer_labels':[{'label':r[0],'records':r[1],'analytics_title_records':r[2],'first_posted':r[3],'last_posted':r[4]} for r in matches]})
        result['status']='ok'
    finally:conn.rollback();conn.close()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--alias',choices=['local','azure'],required=True);a=p.parse_args()
    result=audit(a.alias,dotenv_values(a.env_file))
    out=REVIEW/'reports'/('company-coverage-'+a.alias+'.parquet');out.parent.mkdir(parents=True,exist_ok=True);pq.write_table(pa.Table.from_pylist([result]),out,compression='zstd')
    print(json.dumps({'alias':a.alias,'status':result['status'],'companies':[{k:v for k,v in c.items() if k!='employer_labels'} for c in result['companies']],'tables':result['candidate_tables']}))
