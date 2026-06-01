"""Backup estático via Excel local (último recurso operacional)."""

from __future__ import annotations

import pandas as pd

from titulospub.dados.backup.paths import backup_excel_path
from titulospub.utils.datas import adicionar_dias_uteis, e_dia_util


def backup_cdi() -> float:
    cdi_df = pd.read_excel(backup_excel_path("cdi.xlsx"))
    return float(cdi_df.iloc[0, 0])


def backup_ipca_proj() -> float:
    ipca_proj_df = pd.read_excel(backup_excel_path("ipca_proj.xlsx"))
    return float(ipca_proj_df.iloc[0, 0])


def backup_feriados() -> list:
    feriados_df = pd.read_excel(backup_excel_path("feriados.xlsx"))
    feriados_df["FERIADOS"] = pd.to_datetime(feriados_df["FERIADOS"])
    return feriados_df["FERIADOS"].tolist()


def backup_ipca_fechado() -> pd.DataFrame:
    ipca_fechado_df = pd.read_excel(backup_excel_path("ipca_fechado.xlsx"))
    ipca_fechado_df["DATA"] = ipca_fechado_df["DATA"].astype(str)
    ipca_fechado_df["DATA_CODIGO"] = ipca_fechado_df["DATA_CODIGO"].astype(str)
    ipca_fechado_df["MEDIDA"] = ipca_fechado_df["MEDIDA"].astype(str)
    ipca_fechado_df["VALOR"] = ipca_fechado_df["VALOR"].astype(float)
    return ipca_fechado_df


def backup_anbimas() -> dict[str, pd.DataFrame]:
    anbimas_df = pd.read_excel(backup_excel_path("anbimas.xlsx"))
    anbimas_df = anbimas_df.drop(index=0)
    anbimas_df = anbimas_df[
        ["Código SELIC", "Data de Vencimento", "Tx. Indicativas", "PU"]
    ]

    titulos = {
        100000: "LTN",
        770100: "NTN-C",
        210100: "LFT",
        760199: "NTN-B",
        950199: "NTN-F",
    }

    anbimas_df["Código SELIC"] = anbimas_df["Código SELIC"].replace(titulos)

    colunas = {
        "Código SELIC": "TITULO",
        "Data de Vencimento": "VENCIMENTO",
        "Tx. Indicativas": "ANBIMA",
    }

    anbimas_df = anbimas_df.rename(columns=colunas)
    anbimas_df["DATA"] = pd.Timestamp.today().normalize()
    anbimas_df["VENCIMENTO"] = pd.to_datetime(anbimas_df["VENCIMENTO"])
    anbimas_df = anbimas_df[["TITULO", "DATA", "VENCIMENTO", "ANBIMA", "PU"]]
    anbimas_df = anbimas_df.reset_index(drop=True)

    return {
        titulo: anbimas_df[anbimas_df["TITULO"] == titulo].reset_index(drop=True)
        for titulo in titulos.values()
    }


def backup_bmf() -> dict[str, pd.DataFrame]:
    bmf_path = backup_excel_path("bmf.xlsx")
    bmf_di_df = pd.read_excel(bmf_path, sheet_name="DI")
    bmf_dap_df = pd.read_excel(bmf_path, sheet_name="DAP")

    bmf_dict: dict[str, pd.DataFrame] = {"DI": bmf_di_df, "DAP": bmf_dap_df}

    nomes = {
        "F": "01",
        "G": "02",
        "H": "03",
        "J": "04",
        "K": "05",
        "M": "06",
        "N": "07",
        "Q": "08",
        "U": "09",
        "V": "10",
        "X": "11",
        "Z": "12",
    }

    for nome, df in bmf_dict.items():
        df.columns = df.columns.str.strip().str.upper()
        if "VENCTO" not in df.columns:
            continue
        if nome == "DI":
            df["DATA_VENCIMENTO"] = df["VENCTO"].astype(str).apply(
                lambda x: f"20{x[1:]}-{nomes.get(x[0], x[0])}-01"
            )
            df[nome] = "DI1" + df["VENCTO"].astype(str)
        else:
            df["DATA_VENCIMENTO"] = df["VENCTO"].astype(str).apply(
                lambda x: f"20{x[1:]}-{nomes.get(x[0], x[0])}-15"
            )
            df[nome] = "DAP" + df["VENCTO"].astype(str)

        df["DATA_VENCIMENTO"] = pd.to_datetime(df["DATA_VENCIMENTO"])
        df["DATA_VENCIMENTO"] = df["DATA_VENCIMENTO"].apply(
            lambda x: x if e_dia_util(x) else adicionar_dias_uteis(x, 1)
        )
        df["DATA"] = pd.Timestamp.today().normalize()
        df["ADJ"] = df["ÚLT. PREÇO"]
        df = df[["DATA", "DATA_VENCIMENTO", nome, "ADJ"]]
        bmf_dict[nome] = df

    return bmf_dict
