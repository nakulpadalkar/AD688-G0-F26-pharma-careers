from snapshot_io import read_snapshot, write_snapshot
"""Explicit, bounded read-only Azure export of public Urban/Census reference data."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import psycopg2
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
DATASET = '11_mobility-metrics_county_longitudinal'

def main():
    p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);a=p.parse_args()
    env=dotenv_values(a.env_file);prefix='DB_' if env.get('LOCAL_DB_HOST') else 'AZURE_DB_'
    assert env.get(prefix+'HOST','').lower().rstrip('.').endswith('.postgres.database.azure.com')
    cfg={k:env.get(prefix+v) for k,v in [('host','HOST'),('port','PORT'),('dbname','NAME'),('user','USER'),('password','PASSWORD')]}
    conn=psycopg2.connect(**cfg,sslmode='require',connect_timeout=15,application_name='pharma_public_county_readonly',options='-c default_transaction_read_only=on -c statement_timeout=90000 -c lock_timeout=3000')
    conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
    try:
        with conn.cursor() as q:
            q.execute("select current_setting('transaction_read_only')");assert q.fetchone()[0]=='on'
            q.execute('select checksum,commit,manifest from met_career_match_urbanmobilityrelease where is_active=true')
            releases=q.fetchall();assert len(releases)==1
            release,commit,manifest=releases[0]
            q.execute('select year,count(*) filter (where "values" ? %s) from met_career_match_urbanmobilityobservation where release_id=%s and dataset=%s and subgroup_type=%s and subgroup=%s group by year order by year desc',('share_employed',release,DATASET,'all','All'))
            coverage=q.fetchall();year=next(y for y,n in coverage if n)
            q.execute('select geoid,name,state_name,in_universe,"values",source_row from met_career_match_urbanmobilityobservation where release_id=%s and dataset=%s and year=%s and subgroup_type=%s and subgroup=%s order by geoid limit 5001',(release,DATASET,year,'all','All'))
            raw=q.fetchall();assert len(raw)<=5000
            rows=[]
            for geoid,name,state_name,universe,values,line in raw:
                r={'geoid':geoid,'name':name,'state_name':state_name,'in_universe':universe,'source_row':line}
                for key in ['share_employed','share_employed_lb','share_employed_ub','share_employed_quality']:
                    r[key]=values.get(key)
                rows.append(r)
            q.execute("select geoid,name,geometry from met_career_match_censusboundarygeometry where layer='county' and vintage=2025 and scale='5m' order by geoid limit 5001")
            boundaries=[{'geoid':g,'name':n,'geometry':v} for g,n,v in q.fetchall()];assert 3000<len(boundaries)<=5000
            q.execute("select distinct source_name from met_career_match_censusboundarygeometry where layer='county' and vintage=2025 and scale='5m'")
            boundary_sources=[r[0] for r in q.fetchall()]
        entry=next(x for x in manifest['files'] if Path(x['path']).stem==DATASET)
        out=ROOT/'outputs/market-visuals/data';out.mkdir(parents=True,exist_ok=True)
        payload={'release':release,'commit':commit,'dataset':DATASET,'year':year,'source_url':entry['url'],'source_sha256':entry['sha256'],'license':manifest['license'],'source_retrieved_at':manifest['retrieved_at'],'exported_at':datetime.now(timezone.utc).isoformat(),'database_alias':'azure','transaction_read_only':True,'coverage_by_year':coverage,'boundary_vintage':2025,'boundary_scale':'5m','boundary_sources':boundary_sources,'rows':rows}
        write_snapshot(out/'urban-counties.parquet',payload)
        write_snapshot(out/'county-boundaries.parquet',boundaries)
        print(json.dumps({'year':year,'rows':len(rows),'boundaries':len(boundaries),'readonly':True,'release':release}))
    finally:conn.rollback();conn.close()

if __name__=='__main__': main()
