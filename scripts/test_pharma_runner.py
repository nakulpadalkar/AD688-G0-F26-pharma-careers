"""Exercise cohort boundaries and resume behavior without invoking any DB code."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import run_pharma_enrichment as runner

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);folder=root/'outputs/training-market/enrichment';folder.mkdir(parents=True)
    ids=list(range(1,106));path=folder/'pending-ids.json';path.write_text(json.dumps(ids))
    (folder/'manifest.json').write_text(json.dumps({'pending_ids':len(ids),'ids_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
    service=root/'service';files=['scripts/run_job_enrichment_stage.py','met_career_match/services/job_stage_runtime.py']+[f'scripts/job_stages/{s}.py' for s in runner.STAGES]
    for name in files:
        f=service/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('# test fixture only')
    calls=[]
    def fake_run(command,**kwargs):
        batch=json.loads(Path(command[command.index('--ids-file')+1]).read_text())
        assert set(batch)<=set(ids) and 1<=len(batch)<=100
        stage=command[command.index('--stage')+1];calls.append((stage,batch))
        receipt=Path(command[command.index('--receipt')+1]);assert not receipt.exists()
        receipt.write_text(json.dumps({'job_ids':batch,'target':'local','azure_writes':False,'status':'complete'}))
        return SimpleNamespace(returncode=0)
    def invoke(execute):
        argv=['run','--service-repo',str(service),'--max-batches','1']+(['--execute'] if execute else [])
        with patch.object(runner,'ROOT',root),patch.object(runner.sys,'argv',argv),patch.object(runner.subprocess,'run',fake_run),redirect_stdout(io.StringIO()):runner.main()
    invoke(False);assert not calls
    invoke(True);assert len(calls)==len(runner.STAGES) and all(batch==ids[:100] for _,batch in calls)
    invoke(True);assert len(calls)==2*len(runner.STAGES) and all(batch==ids[100:] for _,batch in calls[len(runner.STAGES):])
    invoke(True);assert len(calls)==2*len(runner.STAGES)
    path.write_text(json.dumps(ids+[9999]))
    try:invoke(True)
    except AssertionError:pass
    else:raise AssertionError('Changed cohort was not rejected')
print('SCOPED_RUNNER_OK: plan-only default, exact IDs, batches <=100, immutable receipts, resume and changed-cohort rejection; no DB calls')
