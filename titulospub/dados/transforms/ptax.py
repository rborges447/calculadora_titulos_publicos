"""Normalização de PTAX a partir do gold ``ptax`` do bbdb."""

from __future__ import annotations

import pandas as pd


def transform_ptax(df: pd.DataFrame) -> float:
    """Gold ``ptax`` (1 linha) → contrato ``float`` (PTAX venda)."""
    if df is None or df.empty:
        raise ValueError("ptax: DataFrame vazio")
    if "ptax_venda" not in df.columns:
        raise ValueError(
            f"ptax: coluna 'ptax_venda' ausente; colunas: {list(df.columns)}"
        )

    work = df.copy()
    return float(work["ptax_venda"].iloc[0])


def ptax_from_db(data: pd.Timestamp | str) -> float:
    from titulospub.dados.db_reader import get_reader

    data_str = pd.Timestamp(data).strftime("%Y-%m-%d")
    df = get_reader().ptax.fetch_on(data_str)
    if df is None or df.empty:
        raise ValueError(
            f"ptax: sem dados no banco para data={data_str}. "
            "Execute bbdb.update e materialize o gold ptax até essa data."
        )
    return transform_ptax(df)
