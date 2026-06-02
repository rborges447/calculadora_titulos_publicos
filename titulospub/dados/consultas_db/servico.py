"""Orquestração de consultas exploratórias ao gold bbdb."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import pandas as pd

from titulospub.dados.db_reader import get_db_path, get_reader

from .catalogo import FonteConsulta, obter_fonte
from .disponibilidade import obter_intervalo_disponivel
from .excecoes import (
    BancoIndisponivelError,
    ColunasInvalidasError,
    IntervaloSemDadosError,
    LimiteExportacaoError,
)
from .formatacao import (
    CSV_ENCODING,
    CSV_SEPARADOR_CAMPOS,
    formatar_dataframe_para_csv_pt_br,
)
from .serializacao import serializar_dataframe

LIMITE_PREVIEW_PADRAO = 5000
LIMITE_MAX_EXPORTACAO = 500_000


@dataclass(frozen=True, slots=True)
class IntervaloContext:
    """Metadados do intervalo pedido vs. efetivo vs. disponível no DB."""

    data_inicio_efetiva: str | None
    data_fim_efetiva: str | None
    data_disponivel_inicio: str | None
    data_disponivel_fim: str | None
    intervalo_ajustado: bool
    mensagem_aviso: str | None


@dataclass(frozen=True, slots=True)
class ConsultaResultado:
    """Resultado de ``consultar`` para API/UI."""

    tabela: str
    data_inicio: str | None
    data_fim: str | None
    colunas: list[str]
    total_linhas: int
    truncado: bool
    rows: list[dict[str, Any]]
    data_inicio_efetiva: str | None = None
    data_fim_efetiva: str | None = None
    data_disponivel_inicio: str | None = None
    data_disponivel_fim: str | None = None
    intervalo_ajustado: bool = False
    mensagem_aviso: str | None = None


def consultar(
    tabela: str,
    colunas: list[str],
    data_inicio: str | None = None,
    data_fim: str | None = None,
    *,
    limite_preview: int = LIMITE_PREVIEW_PADRAO,
) -> ConsultaResultado:
    """Consulta gold com preview limitado.

    A ordem das colunas no resultado segue o parâmetro ``colunas``.
    """
    fonte = obter_fonte(tabela)
    df, intervalo = _carregar_e_projetar(fonte, colunas, data_inicio, data_fim)
    total_linhas = len(df)
    truncado = total_linhas > limite_preview
    df_preview = df.head(limite_preview) if truncado else df
    return ConsultaResultado(
        tabela=tabela,
        data_inicio=data_inicio,
        data_fim=data_fim,
        colunas=list(colunas),
        total_linhas=total_linhas,
        truncado=truncado,
        rows=serializar_dataframe(df_preview),
        data_inicio_efetiva=intervalo.data_inicio_efetiva,
        data_fim_efetiva=intervalo.data_fim_efetiva,
        data_disponivel_inicio=intervalo.data_disponivel_inicio,
        data_disponivel_fim=intervalo.data_disponivel_fim,
        intervalo_ajustado=intervalo.intervalo_ajustado,
        mensagem_aviso=intervalo.mensagem_aviso,
    )


def exportar_csv(
    tabela: str,
    colunas: list[str],
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> tuple[bytes, str]:
    """Exporta o recorte completo em CSV UTF-8 com BOM."""
    fonte = obter_fonte(tabela)
    df, intervalo = _carregar_e_projetar(fonte, colunas, data_inicio, data_fim)
    total_linhas = len(df)
    if total_linhas > LIMITE_MAX_EXPORTACAO:
        raise LimiteExportacaoError(total_linhas, LIMITE_MAX_EXPORTACAO)

    df_export = formatar_dataframe_para_csv_pt_br(df)
    buffer = io.StringIO()
    df_export.to_csv(
        buffer,
        index=False,
        sep=CSV_SEPARADOR_CAMPOS,
        na_rep="",
        quoting=csv.QUOTE_MINIMAL,
    )
    conteudo = buffer.getvalue().encode(CSV_ENCODING)
    inicio_nome = intervalo.data_inicio_efetiva or data_inicio
    fim_nome = intervalo.data_fim_efetiva or data_fim
    nome = _nome_arquivo_csv(tabela, inicio_nome, fim_nome, fonte)
    return conteudo, nome


def _carregar_e_projetar(
    fonte: FonteConsulta,
    colunas: list[str],
    data_inicio: str | None,
    data_fim: str | None,
) -> tuple[pd.DataFrame, IntervaloContext]:
    _validar_colunas(fonte, colunas)
    inicio, fim = _parse_intervalo(fonte, data_inicio, data_fim)
    inicio, fim, intervalo = _resolver_intervalo_efetivo(fonte, inicio, fim)
    df = _ler_dataframe(fonte, inicio, fim)
    if (
        fonte.modo == "snapshot"
        and fonte.coluna_data is not None
        and inicio is not None
        and fim is not None
    ):
        df = _filtrar_por_data(df, fonte.coluna_data, inicio, fim)
    return df[colunas], intervalo


def _validar_colunas(fonte: FonteConsulta, colunas: list[str]) -> None:
    if not colunas:
        raise ColunasInvalidasError(fonte.id)
    permitidas = set(fonte.colunas)
    invalidas = [c for c in colunas if c not in permitidas]
    if invalidas:
        raise ColunasInvalidasError(fonte.id, colunas_invalidas=invalidas)


def _parse_intervalo(
    fonte: FonteConsulta,
    data_inicio: str | None,
    data_fim: str | None,
) -> tuple[date | None, date | None]:
    if fonte.modo == "range":
        if not data_inicio or not data_fim:
            raise ValueError(
                f"Fonte '{fonte.id}' exige data_inicio e data_fim (YYYY-MM-DD)."
            )
        inicio = _parse_data_iso(data_inicio, "data_inicio")
        fim = _parse_data_iso(data_fim, "data_fim")
        if inicio > fim:
            raise ValueError(
                f"data_inicio ({data_inicio}) deve ser <= data_fim ({data_fim})."
            )
        return inicio, fim

    if fonte.coluna_data is None:
        return None, None

    if data_inicio is None and data_fim is None:
        return None, None

    if not data_inicio or not data_fim:
        raise ValueError(
            f"Para filtrar '{fonte.id}' informe data_inicio e data_fim, ou omita ambos."
        )
    inicio = _parse_data_iso(data_inicio, "data_inicio")
    fim = _parse_data_iso(data_fim, "data_fim")
    if inicio > fim:
        raise ValueError(
            f"data_inicio ({data_inicio}) deve ser <= data_fim ({data_fim})."
        )
    return inicio, fim


def _resolver_intervalo_efetivo(
    fonte: FonteConsulta,
    inicio: date | None,
    fim: date | None,
) -> tuple[date | None, date | None, IntervaloContext]:
    if fonte.coluna_data is None or (inicio is None and fim is None):
        disp_min, disp_max = (
            obter_intervalo_disponivel(fonte) if fonte.coluna_data else (None, None)
        )
        return inicio, fim, IntervaloContext(
            data_inicio_efetiva=_iso(inicio),
            data_fim_efetiva=_iso(fim),
            data_disponivel_inicio=_iso(disp_min),
            data_disponivel_fim=_iso(disp_max),
            intervalo_ajustado=False,
            mensagem_aviso=None,
        )

    assert inicio is not None and fim is not None
    disp_min, disp_max = obter_intervalo_disponivel(fonte)

    if disp_min is None or disp_max is None:
        raise IntervaloSemDadosError(
            fonte.id,
            pedido_inicio=_iso(inicio),
            pedido_fim=_iso(fim),
            sem_dados_na_fonte=True,
        )

    eff_inicio = max(inicio, disp_min)
    eff_fim = min(fim, disp_max)

    if eff_inicio > eff_fim:
        raise IntervaloSemDadosError(
            fonte.id,
            pedido_inicio=_iso(inicio),
            pedido_fim=_iso(fim),
            disponivel_inicio=_iso(disp_min),
            disponivel_fim=_iso(disp_max),
        )

    ajustado = eff_inicio != inicio or eff_fim != fim
    mensagem = None
    if ajustado:
        mensagem = (
            f"Período ajustado: solicitado {_iso(inicio)} a {_iso(fim)}; "
            f"no banco há dados entre {_iso(disp_min)} e {_iso(disp_max)}. "
            f"Exibindo {_iso(eff_inicio)} a {_iso(eff_fim)}."
        )

    return (
        eff_inicio,
        eff_fim,
        IntervaloContext(
            data_inicio_efetiva=_iso(eff_inicio),
            data_fim_efetiva=_iso(eff_fim),
            data_disponivel_inicio=_iso(disp_min),
            data_disponivel_fim=_iso(disp_max),
            intervalo_ajustado=ajustado,
            mensagem_aviso=mensagem,
        ),
    )


def _iso(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _parse_data_iso(value: str, param: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{param} inválida: '{value}' (use YYYY-MM-DD).") from exc


def _ler_dataframe(
    fonte: FonteConsulta,
    inicio: date | None,
    fim: date | None,
) -> pd.DataFrame:
    try:
        reader = get_reader()
    except FileNotFoundError:
        raise BancoIndisponivelError(get_db_path()) from None

    table = getattr(reader, fonte.reader_attr)
    if fonte.modo == "range":
        assert inicio is not None and fim is not None
        return table.fetch_range(inicio.isoformat(), fim.isoformat())
    return table.fetch_all()


def _filtrar_por_data(
    df: pd.DataFrame,
    coluna_data: str,
    inicio: date,
    fim: date,
) -> pd.DataFrame:
    if df.empty:
        return df
    serie = pd.to_datetime(df[coluna_data]).dt.normalize()
    mask = serie.between(pd.Timestamp(inicio), pd.Timestamp(fim))
    return df.loc[mask]


def _nome_arquivo_csv(
    tabela: str,
    data_inicio: str | None,
    data_fim: str | None,
    fonte: FonteConsulta,
) -> str:
    if data_inicio and data_fim:
        return f"{tabela}_{data_inicio}_{data_fim}.csv"
    if fonte.modo == "snapshot":
        return f"{tabela}_snapshot.csv"
    return f"{tabela}.csv"
