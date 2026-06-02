"""Smoke tests do pacote consultas_db (Fase 0 — exceções)."""

from __future__ import annotations

from pathlib import Path

import pytest

from titulospub.dados.consultas_db import (
    BancoIndisponivelError,
    ColunasInvalidasError,
    ConsultaDbError,
    IntervaloSemDadosError,
    LimiteExportacaoError,
    TabelaDesconhecidaError,
)


@pytest.mark.parametrize(
    "cls",
    [
        TabelaDesconhecidaError,
        ColunasInvalidasError,
        BancoIndisponivelError,
        LimiteExportacaoError,
        IntervaloSemDadosError,
    ],
)
def test_subclasses_herdam_consulta_db_error(cls: type[Exception]) -> None:
    assert issubclass(cls, ConsultaDbError)


def test_tabela_desconhecida_preserva_atributo() -> None:
    err = TabelaDesconhecidaError("cdi_typo")
    assert err.tabela == "cdi_typo"
    assert "cdi_typo" in str(err)


def test_colunas_invalidas_lista_vazia() -> None:
    err = ColunasInvalidasError("cdi")
    assert err.tabela == "cdi"
    assert err.colunas_invalidas == ()
    assert "Nenhuma coluna" in str(err)


def test_colunas_invalidas_com_nomes() -> None:
    err = ColunasInvalidasError("cdi", colunas_invalidas=["foo", "bar"])
    assert err.colunas_invalidas == ("foo", "bar")
    assert "foo" in str(err)


def test_banco_indisponivel_com_path() -> None:
    err = BancoIndisponivelError("/tmp/app.db")
    assert err.path == Path("/tmp/app.db").resolve()
    assert "BBDB_DB_PATH" in str(err)


def test_limite_exportacao_atributos() -> None:
    err = LimiteExportacaoError(600_000, 500_000)
    assert err.total_linhas == 600_000
    assert err.limite == 500_000
    assert "500,000" in str(err)
