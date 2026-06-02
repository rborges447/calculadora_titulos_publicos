"""Serialização de DataFrames para resposta JSON."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def serializar_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Converte ``DataFrame`` em lista de dicts JSON-safe (datas ISO, NaN → null)."""
    if df.empty:
        return []

    work = df.copy()
    for col in work.columns:
        if pd.api.types.is_datetime64_any_dtype(work[col]):
            work[col] = work[col].dt.strftime("%Y-%m-%d")
        elif work[col].dtype == object:
            sample = work[col].dropna()
            if not sample.empty and isinstance(sample.iloc[0], (pd.Timestamp,)):
                work[col] = pd.to_datetime(work[col]).dt.strftime("%Y-%m-%d")

    records: list[dict[str, Any]] = []
    for row in work.to_dict(orient="records"):
        records.append({k: _json_value(v) for k, v in row.items()})
    return records


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return value
