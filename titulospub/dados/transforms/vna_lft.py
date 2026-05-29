"""Normalização de VNA LFT a partir do gold ``vna`` do bbdb."""

from __future__ import annotations

import pandas as pd

_CODIGO_SELIC_LFT = 210100


def transform_vna_lft(df: pd.DataFrame) -> float:
    """Gold ``vna`` (várias linhas) → contrato Spec 001 ``float`` (VNA LFT)."""
    if df is None or df.empty:
        raise ValueError("vna_lft: DataFrame vazio")
    if "codigo_selic" not in df.columns:
        raise ValueError(
            f"vna_lft: coluna 'codigo_selic' ausente; colunas: {list(df.columns)}"
        )
    if "vna" not in df.columns:
        raise ValueError(f"vna_lft: coluna 'vna' ausente; colunas: {list(df.columns)}")

    work = df.copy()
    lft = work[work["codigo_selic"].astype(int) == _CODIGO_SELIC_LFT]
    if lft.empty:
        raise ValueError(
            f"vna_lft: LFT (codigo_selic {_CODIGO_SELIC_LFT}) não encontrado"
        )
    if len(lft) > 1:
        raise ValueError(
            f"vna_lft: múltiplas linhas LFT (codigo_selic {_CODIGO_SELIC_LFT})"
        )
    return float(lft["vna"].iloc[0])


def vna_lft_from_db(data: pd.Timestamp | str) -> float:
    from titulospub.dados.db_reader import get_reader

    data_str = pd.Timestamp(data).strftime("%Y-%m-%d")
    df = get_reader().vna.fetch_on(data_str)
    if df is None or df.empty:
        raise ValueError(
            f"vna_lft: sem dados no banco para data={data_str}. "
            "Execute bbdb.update e materialize o gold vna até essa data."
        )
    return transform_vna_lft(df)
