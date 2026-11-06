"""Read back only the pinned pending cohort; compare actual field coverage."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from local_pg import connect

ROOT=Path(__file__).resolve().parents[1]
FIELDS=['enrichment_status','naics_code','soc_code','onet_code','countryiso','state_code','jobhive_company_id','requirements_summary','technical_tools_summary','annual_salary_min','annual_salary_max','bls_annual_median_wage','bls_source_year','posted_at','alive_checked_at']


def main():
    p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--label',choices=['before','after'],required=True);args=p.parse_args()
    folder=ROOT/'outputs/training-market/enrichment'
    manifest=json.loads((folder/'manifest.json').read_text());path=folder/'pending-ids.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['ids_sha256']
    ids=json.loads(path.read_text());target=folder/f'{args.label}-coverage.json'
    assert not target.exists(),'Coverage receipts are immutable; preserve the existing receipt'
    counts=Counter();statuses=Counter();found=0
    conn=connect(args.env_file)
    try:
        with conn.cursor() as q:
            for offset in range(0,len(ids),2000):
                q.execute('SELECT '+','.join(FIELDS)+' FROM met_career_match_jobposting WHERE id=ANY(%s)',(ids[offset:offset+2000],))
                for values in q.fetchall():
                    row=dict(zip(FIELDS,values));found+=1;statuses[row['enrichment_status'] or 'missing']+=1
                    counts.update(k for k,v in row.items() if v is not None and v!='')
        result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'read_only':True,'ids_sha256':manifest['ids_sha256'],
                'requested_ids':len(ids),'found_ids':found,'missing_ids':len(ids)-found,'statuses':dict(statuses),'nonempty_field_counts':dict(counts),
                'interpretation':'Nonempty fields and pipeline status are coverage measures, not independent correctness validation.'}
        if args.label=='after':
            before=json.loads((folder/'before-coverage.json').read_text());assert before['ids_sha256']==result['ids_sha256']
            result['field_count_changes']={k:counts[k]-before['nonempty_field_counts'].get(k,0) for k in FIELDS}
            result['pending_change']=statuses['pending']-before['statuses'].get('pending',0)
        target.write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result))
    finally:conn.rollback();conn.close()


if __name__=='__main__':main()
