import os
import json
import pandas as pd
from typing import List, Dict, IO

def write_parquet_path(logs: List[Dict], path: str):
    """
    Write validated logs to a parquet file at 'path' (filesystem).
    """
    if not logs:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(logs)
    df.to_parquet(path, engine="pyarrow", index=False)

def write_parquet_buffer(logs: List[Dict], buffer: IO[bytes]):
    """
    Write validated logs to a file-like object (e.g., BytesIO) in Parquet format.
    """
    if not logs:
        return
    df = pd.DataFrame(logs)
    df.to_parquet(buffer, engine="pyarrow", index=False)

def errors_to_jsonl_str(errors: List[Dict]) -> str:
    """
    Convert list of error dicts into JSON Lines string.
    """
    return "\n".join(json.dumps(e) for e in errors)

def write_errors_path(errors: List[Dict], path: str):
    """
    Write invalid logs to a JSONL file at 'path' (filesystem).
    """
    if not errors:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for e in errors:
            f.write(json.dumps(e) + "\n")
