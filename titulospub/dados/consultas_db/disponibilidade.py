"""Intervalo de datas disponível por fonte no SQLite gold."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime

from titulospub.dados.db_reader import get_db_path

from .catalogo import GOLD_READER_ATTRS, FonteConsulta
from .excecoes import BancoIndisponivelError, TabelaAusenteNoBancoError

# Fontes sem tabela física: intervalo = união das datas nas tabelas base (bbdb readers).
_INTERVALO_FONTES_COMPOSTAS: dict[str, tuple[str, ...]] = {
    "mercado_com_liquidacoes": ("mercado_secundario", "liquidacoes_mercado"),
}


def _resolver_nome_tabela_sqlite(
    conn: sqlite3.Connection, reader_attr: str
) -> str | None:
    """Nome real no SQLite (bbdb usa identificadores em maiúsculas)."""
    row = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type IN ('table', 'view') AND lower(name) = lower(?)",
        (reader_attr,),
    ).fetchone()
    return row[0] if row else None


def _min_max_coluna(
    conn: sqlite3.Connection,
    nome_tabela: str,
    coluna_data: str,
) -> tuple[date | None, date | None]:
    row = conn.execute(
        f'SELECT MIN("{coluna_data}"), MAX("{coluna_data}") FROM "{nome_tabela}"'
    ).fetchone()
    if row is None or (row[0] is None and row[1] is None):
        return None, None
    return _valor_para_date(row[0]), _valor_para_date(row[1])


def _intervalo_fonte_composta(
    conn: sqlite3.Connection,
    fonte: FonteConsulta,
    attrs_base: tuple[str, ...],
) -> tuple[date | None, date | None]:
    coluna = fonte.coluna_data
    assert coluna is not None

    mins: list[date] = []
    maxs: list[date] = []
    tabelas_encontradas: list[str] = []

    for attr in attrs_base:
        nome = _resolver_nome_tabela_sqlite(conn, attr)
        if nome is None:
            continue
        tabelas_encontradas.append(nome)
        dmin, dmax = _min_max_coluna(conn, nome, coluna)
        if dmin is not None:
            mins.append(dmin)
        if dmax is not None:
            maxs.append(dmax)

    if not tabelas_encontradas:
        raise TabelaAusenteNoBancoError(
            fonte.id,
            nome_sql=" + ".join(attrs_base),
        )

    if not mins and not maxs:
        return None, None

    return (min(mins) if mins else None, max(maxs) if maxs else None)


def obter_intervalo_disponivel(fonte: FonteConsulta) -> tuple[date | None, date | None]:
    """Retorna (min, max) da coluna de data no gold, ou (None, None) se não aplicável."""
    if fonte.coluna_data is None:
        return None, None

    if fonte.reader_attr not in GOLD_READER_ATTRS:
        return None, None

    if fonte.coluna_data not in fonte.colunas:
        return None, None

    db_path = get_db_path()
    if not db_path.is_file():
        raise BancoIndisponivelError(db_path)

    try:
        with sqlite3.connect(db_path) as conn:
            attrs_compostos = _INTERVALO_FONTES_COMPOSTAS.get(fonte.reader_attr)
            if attrs_compostos is not None:
                return _intervalo_fonte_composta(conn, fonte, attrs_compostos)

            nome_tabela = _resolver_nome_tabela_sqlite(conn, fonte.reader_attr)
            if nome_tabela is None:
                raise TabelaAusenteNoBancoError(fonte.id, nome_sql=fonte.reader_attr)

            resultado = _min_max_coluna(conn, nome_tabela, fonte.coluna_data)
    except TabelaAusenteNoBancoError:
        raise
    except sqlite3.Error as exc:
        if "no such table" in str(exc).lower():
            raise TabelaAusenteNoBancoError(fonte.id, nome_sql=fonte.reader_attr) from exc
        raise ValueError(
            f"Não foi possível ler disponibilidade de '{fonte.id}': {exc}"
        ) from exc

    if resultado[0] is None and resultado[1] is None:
        return None, None

    return resultado


def _valor_para_date(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return None
    if " " in text:
        text = text.split(" ", 1)[0]
    if "T" in text:
        text = text.split("T", 1)[0]
    return datetime.strptime(text[:10], "%Y-%m-%d").date()
