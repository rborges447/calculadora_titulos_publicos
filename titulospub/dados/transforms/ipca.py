"""Normalização de IPCA dict a partir do gold ``ipca_dict`` do bbdb."""

from __future__ import annotations

import pandas as pd

from titulospub.utils.datas import adicionar_dias_uteis, e_dia_util

_COLUMNS_TO_REMOVE = (
    "data_referencia",
    "ref_month_atual",
    "ref_month_anterior",
    "usa_fechado",
    "data_coleta_referencia",
    "ipca_proj_data_coleta",
    "inicio_mes_ipca",
    "fim_mes_ipca",
)

_COLUMNS_TO_RENAME = {
    "ultimo_mes_ipca": "ULTIMO_MES_IPCA",
    "indice_ipca_data_base": "INDICE_IPCA_DATA_BASE",
    "indice_ipca_fechado_atual": "INDICE_IPCA_FECHADO_ATUAL",
    "indice_ipca_fechado_anterior": "INDICE_IPCA_FECHADO_ANTERIOR",
    "var_ipca_atual": "VAR_IPCA_ATUAL",
    "var_ipca_ant": "VAR_IPCA_ANTERIOR",
    "ipca_proj": "IPCA_PROJ",
    "ipca_usado": "IPCA_USADO",
}

def inicio_fim_mes_ipca(data: pd.Timestamp, feriados=None) -> tuple:
    if feriados is None:
        from titulospub.dados.orquestrador import VariaveisMercado

        vm = VariaveisMercado()
        feriados = vm.get_feriados()

    dia_15_dict = {
        "dia_15_mes_ant": (data - pd.DateOffset(months=1)).replace(day=15).normalize(),
        "dia_15_mes_atual": data.replace(day=15).normalize(),
        "dia_15_mes_prox": (data + pd.DateOffset(months=1)).replace(day=15).normalize(),
    }

    for dia_15 in dia_15_dict:
        if not e_dia_util(data=dia_15_dict[dia_15], feriados=feriados):
            dia_15_dict[dia_15] = adicionar_dias_uteis(
                data=dia_15_dict[dia_15], n_dias=1, feriados=feriados
            )

    if data < dia_15_dict["dia_15_mes_atual"]:
        inicio_mes_ipca = dia_15_dict["dia_15_mes_ant"]
        fim_mes_ipca = dia_15_dict["dia_15_mes_atual"]
    else:
        inicio_mes_ipca = dia_15_dict["dia_15_mes_atual"]
        fim_mes_ipca = dia_15_dict["dia_15_mes_prox"]

    return inicio_mes_ipca, fim_mes_ipca


def transform_ipca(df: pd.DataFrame) -> dict:
    """Gold ``ipca_dict`` (1 linha) → contrato Spec 001 ``IPCA_KEYS``."""
    if df is None or df.empty:
        raise ValueError("ipca_dict: DataFrame vazio")
    if len(df) != 1:
        raise ValueError(
            f"ipca_dict: esperada 1 linha, recebeu {len(df)} "
            f"(data_referencia={df.get('data_referencia', pd.Series(dtype=object)).tolist()})"
        )

    work = df.copy()
    drop_cols = [c for c in _COLUMNS_TO_REMOVE if c in work.columns]
    work.drop(columns=drop_cols, inplace=True)

    missing = set(_COLUMNS_TO_RENAME) - set(work.columns)
    if missing:
        raise ValueError(
            f"ipca_dict: colunas ausentes após drop: {sorted(missing)}; "
            f"disponíveis: {list(work.columns)}"
        )

    work.rename(columns=_COLUMNS_TO_RENAME, inplace=True)
    row = work.iloc[0].to_dict()

    return {
        "ULTIMO_MES_IPCA": int(row["ULTIMO_MES_IPCA"]),
        "INDICE_IPCA_DATA_BASE": float(row["INDICE_IPCA_DATA_BASE"]),
        "INDICE_IPCA_FECHADO_ATUAL": float(row["INDICE_IPCA_FECHADO_ATUAL"]),
        "INDICE_IPCA_FECHADO_ANTERIOR": float(row["INDICE_IPCA_FECHADO_ANTERIOR"]),
        "VAR_IPCA_ATUAL": float(row["VAR_IPCA_ATUAL"]),
        "VAR_IPCA_ANTERIOR": float(row["VAR_IPCA_ANTERIOR"]),
        "IPCA_PROJ": float(row["IPCA_PROJ"]),
        "IPCA_USADO": float(row["IPCA_USADO"]),
    }


def ipca_dict_from_db(data: pd.Timestamp | str) -> dict:
    from titulospub.dados.db_reader import get_reader

    data_str = pd.Timestamp(data).strftime("%Y-%m-%d")
    df = get_reader().ipca_dict.fetch_on(data_str)
    if df is None or df.empty:
        raise ValueError(
            f"ipca_dict: sem dados no banco para data={data_str}. "
            "Execute bbdb.update e materialize o gold ipca_dict até essa data."
        )
    return transform_ipca(df)
