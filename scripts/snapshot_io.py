"""Atomic Parquet snapshots for tabular and nested website evidence."""
import json
from pathlib import Path
import uuid
import pyarrow as pa
import pyarrow.parquet as pq


def read_snapshot(path):
    table=pq.read_table(path);rows=table.to_pylist()
    kind=(table.schema.metadata or {}).get(b'kind',b'list')
    if kind==b'document':return json.loads(rows[0]['document_json'])
    return rows[0] if kind==b'object' else rows


def write_snapshot(path,value):
    path=Path(path);assert path.suffix=='.parquet'
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    kind=b'list' if isinstance(value,list) else b'object'
    def document():
        table=pa.Table.from_pylist([{'document_json':json.dumps(value,ensure_ascii=False)}])
        pq.write_table(table.replace_schema_metadata({b'kind':b'document'}),temp,compression='zstd')
    try:
        try:
            table=pa.Table.from_pylist(value if kind==b'list' else [value])
            pq.write_table(table.replace_schema_metadata({b'kind':kind}),temp,compression='zstd')
            if read_snapshot(temp)!=value:document()
        except (pa.ArrowInvalid,pa.ArrowTypeError,pa.ArrowNotImplementedError):
            document()
        assert read_snapshot(temp)==value,'Parquet round-trip changed the data'
        temp.replace(path)
    finally:
        if temp.exists():temp.unlink()
    return path
