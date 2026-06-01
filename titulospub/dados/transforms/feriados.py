"""Normalização de feriados a partir do snapshot FERIADOS do bbdb."""

from __future__ import annotations

import pandas as pd


def transform_feriados(df: pd.DataFrame) -> list:
    """Normaliza snapshot FERIADOS do bbdb → list de Timestamp."""
    df = df.copy()
    if "data" not in df.columns:
        raise ValueError(f"coluna 'data' ausente; colunas: {list(df.columns)}")
    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    return df["data"].to_list()


def feriados_from_db() -> list:
    from titulospub.dados.db_reader import get_reader

    return transform_feriados(get_reader().feriados.fetch_all())


def feriados_from_scraping() -> list:
    """LEGACY_ACQUISITION — lista de feriados via ANBIMA (rede)."""
    from titulospub.scraping.anbima_scraping import scrap_feriados

    return [pd.Timestamp(d).normalize() for d in scrap_feriados()]
