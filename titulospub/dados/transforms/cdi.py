"""Normalização de CDI a partir do gold ``cdi`` do bbdb."""

from __future__ import annotations

import pandas as pd


def transform_cdi(df: pd.DataFrame) -> float:
    """Gold ``cdi`` (1 linha) → contrato Spec 001 ``float``."""
    if df is None or df.empty:
        raise ValueError("cdi: DataFrame vazio")
    if "cdi" not in df.columns:
        raise ValueError(f"cdi: coluna 'cdi' ausente; colunas: {list(df.columns)}")

    work = df.copy()
    return float(work["cdi"].iloc[0])


def cdi_from_db(data: pd.Timestamp | str) -> float:
    from titulospub.dados.db_reader import get_reader

    data_str = pd.Timestamp(data).strftime("%Y-%m-%d")
    df = get_reader().cdi.fetch_on(data_str)
    if df is None or df.empty:
        raise ValueError(
            f"cdi: sem dados no banco para data={data_str}. "
            "Execute bbdb.update e materialize o gold cdi até essa data."
        )
    return transform_cdi(df)
