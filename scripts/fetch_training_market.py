"""Scan all local postings for broad pharma evidence, with no date/employer/row cap."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from local_pg import connect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/training-market'
DOMAIN = r'pharma|biotech|biopharm|life[- ]scien|clinical research|contract research organi'
FIELDS = ['id','source','external_id','title','normalized_title','company_name','location_text','city','state','state_code','countryiso','country_name','remote_status','employment_type','description','html_description_text','apply_url','company_url','posted_at','created_at','is_active','is_duplicate','duplicate_of_id','naics_code','naics_name','soc_code','onet_code','enrichment_status','classification_confidence','requirements_summary','responsibilities_summary','technical_tools_summary','company_description','jobhive_company_id','is_staffing_agency','alive','alive_checked_at','alive_valid_until','url_observed_status','html_fetched_at']
QUERY = 'SELECT '+','.join('j.'+f for f in FIELDS)+", h.naics_code AS company_naics_code, h.industry_status AS company_industry_status FROM met_career_match_jobposting j LEFT JOIN met_career_match_jobhivecompany h ON h.id=j.jobhive_company_id WHERE j.naics_code LIKE '3254%%' OR j.naics_code LIKE '541714%%' OR h.naics_code LIKE '3254%%' OR h.naics_code LIKE '541714%%' OR j.company_name ~* %(domain)s OR j.company_description ~* %(domain)s OR j.title ~* %(domain)s OR j.description ~* %(domain)s OR j.html_description_text ~* %(domain)s"


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--env-file',required=True);args=parser.parse_args()
    out=OUT/'raw';out.mkdir(parents=True,exist_ok=True)
    conn=connect(args.env_file)
    start=datetime.now(timezone.utc).isoformat()
    names=FIELDS+['company_naics_code','company_industry_status']
    schema=pa.schema([(f,pa.string()) for f in names])
    target=out/'local-candidates.parquet';temporary=out/'local-candidates.partial.parquet'
    counts=Counter();rows=0
    try:
        with conn.cursor() as q:
            q.execute("select count(*),count(distinct nullif(lower(trim(company_name)),'')),count(*) filter(where posted_at is null),min(posted_at)::text,max(posted_at)::text from met_career_match_jobposting")
            total,employers,undated,first,last=q.fetchone()
            print(json.dumps({'database_records':total,'distinct_employer_labels':employers,'missing_posting_date':undated}),flush=True)
        with conn.cursor(name='pharma_all_dates') as q, pq.ParquetWriter(temporary,schema,compression='zstd') as writer:
            q.itersize=2000;q.execute(QUERY,{'domain':DOMAIN})
            while True:
                batch=q.fetchmany(2000)
                if not batch:break
                records=[{k:None if v is None else str(v) for k,v in zip(names,r)} for r in batch]
                writer.write_table(pa.Table.from_pylist(records,schema=schema))
                rows+=len(records)
                counts.update(r['enrichment_status'] or 'missing' for r in records)
                if rows%20000==0:print(json.dumps({'candidate_rows_saved':rows}),flush=True)
        assert pq.read_metadata(temporary).num_rows==rows
        temporary.replace(target)
        receipt={'started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'transaction_read_only':True,'isolation':'REPEATABLE READ','source':'local PostgreSQL only','database_records':total,'database_employer_labels':employers,'database_undated_records':undated,'database_posted_range':[first,last],'candidate_records':rows,'candidate_enrichment_status':dict(counts),'query':QUERY,'parameters':{'domain':DOMAIN},'scope':'All available records and dates, including null posting dates; broad row-level pharma/biotech/life-science/clinical-research signals or NAICS 3254/541714. No employer whitelist or row limit. Keyword and enriched-code matches are screening evidence, not verified industry membership.','raw_sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest()}
        (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
        print(json.dumps({'EXTRACT_OK':rows,'database_records':total,'enrichment_status':dict(counts)}),flush=True)
    finally:conn.rollback();conn.close()


if __name__=='__main__':main()
