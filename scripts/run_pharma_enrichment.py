"""Prepared, bounded exact-ID adapter for the existing local job-stage runner.

Default is plan-only. --execute is for the user to launch under the existing
script-only production-enrichment policy. This adapter never resets statuses.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
STAGES=('process_html','location','employment','organization','profiles','salary','soc','naics','sic','remaining','finalize')


def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--retry-partial',action='store_true')
    p.add_argument('--service-repo',type=Path,default=Path('D:/Repositories/met-employability-services'))
    p.add_argument('--python',default=sys.executable);p.add_argument('--max-batches',type=int,default=1)
    p.add_argument('--minutes-per-stage',type=float,default=12);args=p.parse_args()
    assert args.max_batches>0 and 0<args.minutes_per_stage<=60
    folder=ROOT/'outputs/training-market/enrichment'
    manifest=json.loads((folder/'manifest.json').read_text())
    ids_path=folder/'pending-ids.json'
    assert hashlib.sha256(ids_path.read_bytes()).hexdigest()==manifest['ids_sha256']
    ids=json.loads(ids_path.read_text());assert len(ids)==manifest['pending_ids']==len(set(ids))
    assert all(type(i) is int and i>0 for i in ids)
    runner=args.service_repo/'scripts/run_job_enrichment_stage.py';assert runner.exists()
    plan={'target':'local','azure_writes':False,'scope':'exact pinned pending IDs only','pinned_ids':len(ids),
          'batch_size':100,'max_batches_this_invocation':args.max_batches,'stages':STAGES,
          'execute':args.execute,'excluded_actions':['global backlog repair','status resets','network HTML capture','Azure delivery','cross-cohort deduplication']}
    if not args.execute:print(json.dumps(plan,indent=2));return
    checkpoints=folder/'runs';checkpoints.mkdir(exist_ok=True)
    # Preserve resume identity if any underlying stage implementation changes.
    files=[runner,args.service_repo/'met_career_match/services/job_stage_runtime.py']+[args.service_repo/f'scripts/job_stages/{s}.py' for s in STAGES]
    implementation={str(f.relative_to(args.service_repo)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    contract={'ids_sha256':manifest['ids_sha256'],'implementation':implementation,'stages':list(STAGES)}
    contract_path=checkpoints/'contract.json'
    if contract_path.exists():assert json.loads(contract_path.read_text())==contract,'Runner changed; review receipts before creating a new run root'
    else:contract_path.write_text(json.dumps(contract,indent=2))
    attempted=0
    for offset in range(0,len(ids),100):
        batchdir=checkpoints/f'batch-{offset//100:05d}';batchdir.mkdir(exist_ok=True)
        state_path=batchdir/'state.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {'complete_stages':[],'receipts':[]}
        if all(s in state['complete_stages'] for s in STAGES):continue
        if state.get('attempted_all_stages') and not args.retry_partial:continue
        if attempted>=args.max_batches:break
        attempted+=1
        batchfile=batchdir/'ids.json';chunk=ids[offset:offset+100]
        if batchfile.exists():assert json.loads(batchfile.read_text())==chunk
        else:batchfile.write_text(json.dumps(chunk))
        for stage in STAGES:
            if stage in state['complete_stages']:continue
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            receipt=batchdir/f'{stage}-{stamp}.json'
            command=[args.python,str(runner),'--stage',stage,'--ids-file',str(batchfile),'--receipt',str(receipt),'--minutes',str(args.minutes_per_stage),'--workers','4']
            result=subprocess.run(command,cwd=args.service_repo,check=False)
            if not receipt.exists():raise RuntimeError(f'{stage} produced no receipt; stopped without advancing')
            record=json.loads(receipt.read_text())
            assert record['job_ids']==chunk and record['target']=='local' and record['azure_writes'] is False
            state['receipts'].append(str(receipt))
            if result.returncode==0 and record.get('status')=='complete':state['complete_stages'].append(stage)
            state_path.write_text(json.dumps(state,indent=2))
            if result.returncode not in (0,2):raise RuntimeError(f'{stage} failed; inspect immutable receipt')
        state['attempted_all_stages']=True
        state_path.write_text(json.dumps(state,indent=2))
        print(json.dumps({'batch':offset//100,'stages_complete':len(state['complete_stages']),'fully_finalized':len(state['complete_stages'])==len(STAGES)}),flush=True)
    print('Run finished. Stage receipts are attempts, not a count of cleared records. Read back exact pinned IDs before reporting completion.')


if __name__=='__main__':main()
