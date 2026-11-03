"""Task-scoped Parquet storage; generated JS is only a browser delivery format."""
import json
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[1]
TASK=ROOT/'outputs/us-employer-inventory'
REFERENCE=ROOT/'outputs/site-reference'
REVIEW=ROOT/'outputs/employer-page-review'
def artifact_path(name):
 stem=Path(name).stem
 base=TASK/'curated' if stem in ['database-jobs','us-jobs','inventory-summary','employer-analysis','all-employer-records'] else REVIEW/'data' if stem in ['current-jobs','reviewed-examples'] else REFERENCE/'data'
 return base/(stem+'.parquet')
def write_data(name,value):
 path=artifact_path(name);path.parent.mkdir(parents=True,exist_ok=True)
 kind='list' if isinstance(value,list) else 'object'
 try:table=pa.Table.from_pylist(value if kind=='list' else [value]);table.validate(full=True)
 except (pa.ArrowInvalid,pa.ArrowTypeError):
  # Legacy mixed-type document snapshots retain their exact types in a compressed document cell.
  kind='document';table=pa.Table.from_pylist([{'document_json':json.dumps(value,ensure_ascii=False)}])
 table=table.replace_schema_metadata({b'kind':kind.encode()})
 try:pq.write_table(table,path,compression='zstd')
 except pa.ArrowNotImplementedError:
  table=pa.Table.from_pylist([{'document_json':json.dumps(value,ensure_ascii=False)}]).replace_schema_metadata({b'kind':b'document'});pq.write_table(table,path,compression='zstd')
 if read_data(name)!=value:
  table=pa.Table.from_pylist([{'document_json':json.dumps(value,ensure_ascii=False)}]).replace_schema_metadata({b'kind':b'document'});pq.write_table(table,path,compression='zstd')
 assert read_data(name)==value
 return path
def read_data(name):
 table=pq.read_table(artifact_path(name));rows=table.to_pylist();kind=(table.schema.metadata or {}).get(b'kind',b'list')
 return json.loads(rows[0]['document_json']) if kind==b'document' else rows[0] if kind==b'object' else rows
