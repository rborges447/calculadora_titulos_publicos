"""Normalização de PTAX a partir do gold ``ptax`` do bbdb."""

from __future__ import annotations

import pandas as pd


from titulospub.utils.datas import fetch_on_or_prior


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

    df = fetch_on_or_prior(get_reader().ptax, data, variable="ptax")
    return transform_ptax(df)
