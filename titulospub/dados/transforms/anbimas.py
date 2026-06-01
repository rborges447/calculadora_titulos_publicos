"""Normalização de ANBIMAs a partir do gold ``mercado_com_liquidacoes`` do bbdb."""

from __future__ import annotations

import pandas as pd

ANBIMAS_DB_COLUMN_MAP = {
    "tipo_titulo": "TITULO",
    "data_referencia": "DATA",
    "data_vencimento": "VENCIMENTO",
    "taxa_anbima": "ANBIMA",
    "pu": "PU",
    "qtd_titulos": "QTD_OPERADA",
}

ANBIMAS_CONTRACT_COLS = [
    "TITULO",
    "DATA",
    "VENCIMENTO",
    "ANBIMA",
    "PU",
    "QTD_OPERADA",
]


def transform_anbimas(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Gold ``mercado_com_liquidacoes`` → contrato ``dict[str, DataFrame]``."""
    if df is None or df.empty:
        raise ValueError("anbimas: DataFrame vazio")

    missing = set(ANBIMAS_DB_COLUMN_MAP.keys()) - set(df.columns)
    if missing:
        raise ValueError(
            f"anbimas: colunas ausentes no gold: {sorted(missing)}; "
            f"colunas: {list(df.columns)}"
        )

    work = df.loc[df["taxa_anbima"].notna() & df["pu"].notna(), list(ANBIMAS_DB_COLUMN_MAP.keys())].copy()
    if work.empty:
        raise ValueError("anbimas: nenhuma linha de mercado secundário após filtro")

    work = work.rename(columns=ANBIMAS_DB_COLUMN_MAP)
    work["DATA"] = pd.to_datetime(work["DATA"]).dt.normalize()
    work["VENCIMENTO"] = pd.to_datetime(work["VENCIMENTO"]).dt.normalize()
    work["TITULO"] = work["TITULO"].astype(str)
    work["ANBIMA"] = work["ANBIMA"].astype(float)
    work["PU"] = work["PU"].astype(float)
    work["QTD_OPERADA"] = work["QTD_OPERADA"].astype(float)
    work = work[ANBIMAS_CONTRACT_COLS]

    dfs_dict: dict[str, pd.DataFrame] = {}
    for titulo in work["TITULO"].unique():
        dfs_dict[titulo] = (
            work[work["TITULO"] == titulo].reset_index(drop=True)
        )
    return dfs_dict


def anbimas_from_db(data: pd.Timestamp | str) -> dict[str, pd.DataFrame]:
    from titulospub.dados.db_reader import get_reader

    data_str = pd.Timestamp(data).strftime("%Y-%m-%d")
    df = get_reader().mercado_com_liquidacoes.fetch_on(data_str)
    if df is None or df.empty:
        raise ValueError(
            f"anbimas: sem dados no banco para data={data_str}. "
            "Execute bbdb.update e materialize mercado_com_liquidacoes até essa data."
        )
    return transform_anbimas(df)


def anbimas_from_scraping(data: pd.Timestamp | str) -> dict[str, pd.DataFrame]:
    """LEGACY_ACQUISITION — mercado ANBIMA via download TXT (rede)."""
    from titulospub.scraping.anbima_scraping import scrap_anbimas

    return transform_anbimas_scraping(scrap_anbimas(pd.Timestamp(data).normalize()))


def transform_anbimas_scraping(anbima_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Normaliza DataFrame cru do arquivo ANBIMA (LEGACY_ACQUISITION)."""
    colunas = ["Titulo", "Data Referencia", "Data Vencimento", "Tx. Indicativas", "PU"]
    anbima_tratado_df = anbima_df[colunas].copy()

    anbima_tratado_df["Data Referencia"] = pd.to_datetime(
        anbima_tratado_df["Data Referencia"], format="%Y%m%d"
    )
    anbima_tratado_df["Data Vencimento"] = pd.to_datetime(
        anbima_tratado_df["Data Vencimento"], format="%Y%m%d"
    )

    anbima_tratado_df.rename(
        columns={
            "Titulo": "TITULO",
            "Data Referencia": "DATA",
            "Data Vencimento": "VENCIMENTO",
            "Tx. Indicativas": "ANBIMA",
        },
        inplace=True,
    )

    anbima_tratado_df["ANBIMA"] = (
        anbima_tratado_df["ANBIMA"]
        .astype(str)
        .str.replace(r"\.", "", regex=True)
        .str.replace(r",", ".", regex=True)
    ).astype(float)

    anbima_tratado_df["PU"] = (
        anbima_tratado_df["PU"]
        .astype(str)
        .str.replace(r"\.", "", regex=True)
        .str.replace(r",", ".", regex=True)
    ).astype(float)

    dfs_dict: dict[str, pd.DataFrame] = {}
    for titulo in anbima_tratado_df["TITULO"].unique():
        dfs_dict[titulo] = (
            anbima_tratado_df[anbima_tratado_df["TITULO"] == titulo]
            .reset_index(drop=True)
        )
    return dfs_dict


# Alias legado (scraping)
anbimas = transform_anbimas_scraping
