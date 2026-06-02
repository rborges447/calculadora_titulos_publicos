"""Testes do catálogo consultas_db (T-002)."""

from __future__ import annotations

import pytest

from titulospub.dados.consultas_db.catalogo import (
    GOLD_READER_ATTRS,
    iter_fontes,
    listar_catalogo,
    obter_fonte,
)
from titulospub.dados.consultas_db.excecoes import TabelaDesconhecidaError

_CATALOGO_KEYS = frozenset(
    {
        "id",
        "rotulo",
        "reader_attr",
        "modo",
        "coluna_data",
        "colunas",
        "colunas_padrao",
        "descricao",
        "data_disponivel_inicio",
        "data_disponivel_fim",
    }
)


def test_catalogo_tem_12_fontes() -> None:
    fontes = iter_fontes()
    assert len(fontes) == 12
    assert len({f.id for f in fontes}) == 12


def test_colunas_padrao_subset_de_colunas() -> None:
    for fonte in iter_fontes():
        assert set(fonte.colunas_padrao) <= set(fonte.colunas), fonte.id


def test_reader_attr_existe_no_gold_reader() -> None:
    for fonte in iter_fontes():
        assert fonte.reader_attr in GOLD_READER_ATTRS, fonte.id


def test_listar_catalogo_serializavel() -> None:
    catalogo = listar_catalogo()
    assert len(catalogo) == 12
    for item in catalogo:
        assert set(item.keys()) == _CATALOGO_KEYS
        assert isinstance(item["colunas"], list)
        assert isinstance(item["colunas_padrao"], list)
        assert item["modo"] in ("range", "snapshot")


def test_obter_fonte_inexistente() -> None:
    with pytest.raises(TabelaDesconhecidaError) as exc_info:
        obter_fonte("nao_existe")
    assert exc_info.value.tabela == "nao_existe"


def test_obter_fonte_cdi() -> None:
    fonte = obter_fonte("cdi")
    assert fonte.id == "cdi"
    assert fonte.modo == "range"
