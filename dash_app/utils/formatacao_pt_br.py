"""Formatação pt-BR para exibição na UI Dash (Spec 004, espelho do domínio)."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

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


def formatar_inteiro_pt_br(valor: Any) -> str:
    """Formata contagem inteira com separador de milhar pt-BR."""
    return formatar_numero_pt_br(valor, casas_decimais=0)


def formatar_data_exibicao(valor: Any) -> str:
    """Converte data para ``DD/MM/YYYY``."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return ""

    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    if not isinstance(valor, str) and hasattr(valor, "strftime"):
        try:
            return valor.strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            pass
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

    return str(valor)


def _casas_decimais_coluna(nome: str) -> int:
    if nome.startswith("qtd_") or nome.startswith("quantidade_"):
        return 0
    if nome in ("cdi",) or nome.startswith(("taxa_", "ptax_", "pu", "vna", "desvio_")):
        return _CASAS_DECIMAIS_PADRAO
    if nome.startswith(("percentual_", "financeiro_", "oferta")):
        return _CASAS_DECIMAIS_PADRAO
    return _CASAS_DECIMAIS_PADRAO


def _eh_string_iso_data(valor: Any) -> bool:
    if not isinstance(valor, str):
        return False
    texto = valor.strip()
    return (
        len(texto) >= 10
        and texto[4:5] == "-"
        and texto[7:8] == "-"
    )


def formatar_celula_exibicao(coluna: str, valor: Any) -> str:
    """Formata uma célula JSON da API para exibição na DataTable."""
    if valor is None:
        return ""

    if coluna in _COLUNAS_DATA or _eh_string_iso_data(valor):
        return formatar_data_exibicao(valor)

    if isinstance(valor, bool):
        return str(valor)

    if coluna.startswith("qtd_") or coluna.startswith("quantidade_"):
        return formatar_numero_pt_br(valor, casas_decimais=0)

    if isinstance(valor, int):
        return formatar_numero_pt_br(valor, casas_decimais=0)

    if isinstance(valor, float):
        if math.isnan(valor) or math.isinf(valor):
            return ""
        return formatar_numero_pt_br(valor, casas_decimais=_casas_decimais_coluna(coluna))

    return str(valor)


def formatar_rows_para_exibicao(
    colunas: list[str],
    rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Formata linhas JSON da consulta para exibição pt-BR na DataTable."""
    resultado: list[dict[str, str]] = []
    for row in rows:
        formatada: dict[str, str] = {}
        for coluna in colunas:
            formatada[coluna] = formatar_celula_exibicao(coluna, row.get(coluna))
        resultado.append(formatada)
    return resultado
