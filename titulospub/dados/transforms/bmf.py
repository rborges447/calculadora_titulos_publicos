"""Normalização de ajustes BMF (DI/DAP) a partir do gold ``ajustes_bmf`` do bbdb."""

from __future__ import annotations

import pandas as pd

BMF_DB_BASE_MAP = {
    "data_referencia": "DATA",
    "data_vencimento": "DATA_VENCIMENTO",
    "taxa_ajuste": "ADJ",
}

BMF_DB_REQUIRED_COLS = list(BMF_DB_BASE_MAP.keys()) + ["ticker"]

BMF_PREFIXES = {
    "DI": "DI1",
    "DAP": "DAP",
}


def transform_bmf(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Gold ``ajustes_bmf`` → contrato ``dict[str, DataFrame]`` (chaves DI, DAP)."""
    if df is None or df.empty:
        raise ValueError("bmf: DataFrame vazio")

    missing = set(BMF_DB_REQUIRED_COLS) - set(df.columns)
    if missing:
        raise ValueError(
            f"bmf: colunas ausentes no gold: {sorted(missing)}; "
            f"colunas: {list(df.columns)}"
        )

    resultado: dict[str, pd.DataFrame] = {}
    for nome, prefixo in BMF_PREFIXES.items():
        mask = df["ticker"].fillna("").astype(str).str.startswith(prefixo)
        work = df.loc[mask, BMF_DB_REQUIRED_COLS].copy()
        if work.empty:
            raise ValueError(f"bmf: nenhuma linha para contrato {nome} (prefixo {prefixo})")

        work = work.rename(columns={**BMF_DB_BASE_MAP, "ticker": nome})
        work["DATA"] = pd.to_datetime(work["DATA"]).dt.normalize()
        work["DATA_VENCIMENTO"] = pd.to_datetime(work["DATA_VENCIMENTO"]).dt.normalize()
        work[nome] = work[nome].astype(str)
        work["ADJ"] = work["ADJ"].astype(float)
        work = (
            work[["DATA", "DATA_VENCIMENTO", nome, "ADJ"]]
            .sort_values(by="DATA_VENCIMENTO")
            .reset_index(drop=True)
        )
        resultado[nome] = work

    return resultado


def bmf_from_db(data: pd.Timestamp | str) -> dict[str, pd.DataFrame]:
    from titulospub.dados.db_reader import get_reader

    data_str = pd.Timestamp(data).strftime("%Y-%m-%d")
    df = get_reader().ajustes_bmf.fetch_on(data_str)
    if df is None or df.empty:
        raise ValueError(
            f"bmf: sem dados no banco para data={data_str}. "
            "Execute bbdb.update e materialize ajustes_bmf até essa data."
        )
    return transform_bmf(df)


def bmf_from_scraping(data: pd.Timestamp | str) -> dict[str, pd.DataFrame]:
    """LEGACY_ACQUISITION — ajustes DI/DAP via UpToData (rede)."""
    return transform_bmf_scraping(pd.Timestamp(data).normalize())


def transform_bmf_scraping(data) -> dict[str, pd.DataFrame]:
    """Normaliza CSV UpToData (LEGACY_ACQUISITION)."""
    from titulospub.scraping.uptodata_scraping import scrap_ajustes_bmf

    df = scrap_ajustes_bmf(data)
    resultado: dict[str, pd.DataFrame] = {}

    for nome, prefixo in BMF_PREFIXES.items():
        temp_df = df[df["TckrSymb"].fillna("").str.startswith(prefixo)][
            ["RptDt", "XprtnDt", "TckrSymb", "AdjstdQtTax"]
        ]
        temp_df = temp_df.rename(
            columns={
                "RptDt": "DATA",
                "XprtnDt": "DATA_VENCIMENTO",
                "TckrSymb": nome,
                "AdjstdQtTax": "ADJ",
            }
        )

        temp_df["DATA"] = pd.to_datetime(temp_df["DATA"])
        temp_df["DATA_VENCIMENTO"] = pd.to_datetime(temp_df["DATA_VENCIMENTO"])
        temp_df = temp_df.sort_values(by="DATA_VENCIMENTO").reset_index(drop=True)

        resultado[nome] = temp_df

    return resultado


# Alias legado (scraping)
ajustes_bmf = transform_bmf_scraping


def ajustes_bmf_net(bmf_dict, data=None):
    if data is None:
        data = pd.Timestamp.today().normalize()

    bmf_dict_ajustado = {}
    for chave in bmf_dict.keys():
        df = bmf_dict[chave].copy()

        df["DATA"] = data

        renomear = {
            "symb": chave,
            "asset.AsstSummry.mtrtyCode": "DATA_VENCIMENTO",
            "SctyQtn.prvsDayAdjstmntPric": "ADJ",
        }

        df.rename(columns=renomear, inplace=True)

        colunas = ["DATA", "DATA_VENCIMENTO", chave, "ADJ"]

        df = df[colunas]
        df.dropna(inplace=True)
        df["DATA_VENCIMENTO"] = pd.to_datetime(df["DATA_VENCIMENTO"])
        df.sort_values(by="DATA_VENCIMENTO", inplace=True)
        bmf_dict_ajustado[chave] = df
    return bmf_dict_ajustado


if __name__ == "__main__":
    print("Testando processamento BMF...")

    try:
        from titulospub.dados.backup import backup_bmf

        print("Carregando dados BMF de backup...")
        bmf_data = backup_bmf()
        print(f"Dados carregados: {len(bmf_data)} tipos de contratos")

        data = pd.Timestamp.today().normalize()
        processed = transform_bmf_scraping(data)
        print(f"Dados processados: {len(processed)} tipos de contratos")

        for tipo, df_out in processed.items():
            print(f"  - {tipo}: {len(df_out)} registros")
            if len(df_out) > 0:
                print(f"    Colunas: {list(df_out.columns)}")
                print(f"    Primeiro registro: {df_out.iloc[0].to_dict()}")

        print("Processamento BMF funcionando corretamente!")

    except Exception as e:
        print(f"Erro durante teste: {e}")
        import traceback

        traceback.print_exc()
