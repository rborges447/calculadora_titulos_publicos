"""Formatação pt-BR para exibição e exportação CSV (Spec 004)."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

import pandas as pd

CSV_SEPARADOR_CAMPOS = ";"
CSV_ENCODING = "utf-8-sig"

_COLUNAS_DATA: frozenset[str] = frozenset({
    "data",
    "data_referencia",
    "data_vencimento",
    "data_base",
    "data_validade",
    "data_coleta_referencia",
    "ipca_proj_data_coleta",
    "inicio_mes_ipca",
    "fim_mes_ipca",
    "ultimo_mes_ipca",
    "ref_month_atual",
    "ref_month_anterior",
    "data_base_mercado",
    "data_base_liq",
})

_CASAS_DECIMAIS_PADRAO = 6


def formatar_numero_pt_br(valor: Any, *, casas_decimais: int | None = None) -> str:
    """Formata número no padrão brasileiro (milhar ``.``, decimal ``,``)."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return ""
    if pd.isna(valor):
        return ""

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return str(valor)

    if math.isnan(numero) or math.isinf(numero):
        return ""

    if casas_decimais is None:
        casas_decimais = _CASAS_DECIMAIS_PADRAO

    negativo = numero < 0
    abs_num = abs(numero)
    formatado = f"{abs_num:,.{casas_decimais}f}"
    partes = formatado.split(".")
    if len(partes) == 2:
        parte_inteira = partes[0].replace(",", ".")
        parte_decimal = partes[1].rstrip("0")
        if parte_decimal:
            resultado = f"{parte_inteira},{parte_decimal}"
        else:
            resultado = parte_inteira
    else:
        resultado = formatado.replace(",", ".")

    if negativo and resultado not in ("0", ""):
        return f"-{resultado}"
    return resultado


def formatar_data_exibicao(valor: Any) -> str:
    """Converte data para ``DD/MM/YYYY``."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return ""
    if pd.isna(valor):
        return ""

    if isinstance(valor, pd.Timestamp):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return ""
        if len(texto) >= 10 and texto[4:5] == "-" and texto[7:8] == "-":
            try:
                parsed = datetime.strptime(texto[:10], "%Y-%m-%d")
                return parsed.strftime("%d/%m/%Y")
            except ValueError:
                pass
        return texto

    try:
        parsed = pd.to_datetime(valor)
        if pd.isna(parsed):
            return ""
        return parsed.strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return str(valor)


def formatar_dataframe_para_csv_pt_br(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna cópia do DataFrame com células formatadas para CSV pt-BR."""
    if df.empty:
        return df.copy()

    work = df.copy()
    for col in work.columns:
        serie = work[col]
        if _serie_eh_data(col, serie):
            work[col] = serie.map(formatar_data_exibicao)
        elif _serie_eh_inteira(col, serie):
            work[col] = serie.map(
                lambda v: formatar_numero_pt_br(v, casas_decimais=0)
            )
        elif pd.api.types.is_numeric_dtype(serie):
            casas = _casas_decimais_coluna(col)
            work[col] = serie.map(
                lambda v: formatar_numero_pt_br(v, casas_decimais=casas)
            )
        else:
            work[col] = serie.map(_formatar_texto_csv)
    return work


def _formatar_texto_csv(valor: Any) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return ""
    if pd.isna(valor):
        return ""
    return str(valor)


def _serie_eh_data(coluna: str, serie: pd.Series) -> bool:
    if coluna in _COLUNAS_DATA:
        return True
    return pd.api.types.is_datetime64_any_dtype(serie)


def _serie_eh_inteira(coluna: str, serie: pd.Series) -> bool:
    if coluna.startswith("qtd_") or coluna.startswith("quantidade_"):
        return True
    return pd.api.types.is_integer_dtype(serie)


def _casas_decimais_coluna(nome: str) -> int:
    if nome.startswith("qtd_") or nome.startswith("quantidade_"):
        return 0
    if nome in ("cdi",) or nome.startswith(("taxa_", "ptax_", "pu", "vna", "desvio_")):
        return _CASAS_DECIMAIS_PADRAO
    if nome.startswith(("percentual_", "financeiro_", "oferta")):
        return _CASAS_DECIMAIS_PADRAO
    return _CASAS_DECIMAIS_PADRAO
