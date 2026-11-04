"""Dataset I/O with a small, explicit schema boundary."""

from __future__ import annotations

import gzip
import json
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path

import pandas as pd

from .constants import BASE_COLUMN_MAP

BASE_COLUMNS = list(BASE_COLUMN_MAP.values())


def load_table(path: str | Path, sheet_name: str = "总") -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        frame = pd.read_excel(path, sheet_name=sheet_name)
    elif suffix == ".csv":
        frame = pd.read_csv(path)
    elif suffix in {".jsonl", ".json"}:
        frame = pd.read_json(path, lines=suffix == ".jsonl")
    elif suffix == ".parquet":
        frame = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported input format: {suffix}")
    return normalize_base(frame)


def normalize_base(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.rename(columns=BASE_COLUMN_MAP).copy()
    missing = [name for name in BASE_COLUMNS if name not in normalized.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    normalized = normalized[BASE_COLUMNS]
    if normalized[BASE_COLUMNS].isna().any().any():
        nulls = normalized[BASE_COLUMNS].isna().sum()
        raise ValueError(f"Required fields contain nulls: {nulls[nulls > 0].to_dict()}")
    for column in BASE_COLUMNS:
        normalized[column] = normalized[column].astype(str).str.strip()
    return normalized


def read_jsonl(path: str | Path) -> Iterator[dict]:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc


def write_jsonl(records: Iterable[Mapping], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")


def write_table(frame: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        frame.to_parquet(path, index=False, compression="zstd")
    elif suffix == ".jsonl":
        write_jsonl(frame.to_dict(orient="records"), path)
    elif suffix == ".csv":
        frame.to_csv(path, index=False)
    else:
        raise ValueError(f"Unsupported output format: {suffix}")
