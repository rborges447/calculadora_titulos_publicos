"""Normalização de CDI a partir do gold ``cdi`` do bbdb."""

from __future__ import annotations

import pandas as pd


from titulospub.utils.datas import fetch_on_or_prior


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

    df = fetch_on_or_prior(get_reader().cdi, data, variable="cdi")
    return transform_cdi(df)


def cdi_from_scraping(data: pd.Timestamp | str | None = None) -> float:
    """LEGACY_ACQUISITION — CDI estimado ANBIMA (rede; ``data`` ignorado)."""
    from titulospub.scraping.anbima_scraping import scrap_cdi

    return float(scrap_cdi())
