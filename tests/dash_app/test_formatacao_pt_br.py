"""Testes de formatação pt-BR no Dash (Spec 004, T-004)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from dash_app.utils import formatacao_pt_br as fmt
from tests.fixtures.formatacao_pt_br_casos import (
    CASOS_DATA_OBJETOS,
    CASOS_DATA_STRING,
    CASOS_NUMERO,
    CASOS_ROWS,
)


@pytest.mark.regression
@pytest.mark.parametrize(("valor", "casas", "esperado"), CASOS_NUMERO)
def test_formatar_numero_pt_br(valor, casas, esperado) -> None:
    if casas is None:
        assert fmt.formatar_numero_pt_br(valor) == esperado
    else:
        assert fmt.formatar_numero_pt_br(valor, casas_decimais=casas) == esperado


@pytest.mark.regression
@pytest.mark.parametrize(("valor", "esperado"), CASOS_DATA_STRING)
def test_formatar_data_exibicao_string(valor, esperado) -> None:
    assert fmt.formatar_data_exibicao(valor) == esperado


@pytest.mark.regression
@pytest.mark.parametrize(("valor", "esperado"), CASOS_DATA_OBJETOS)
def test_formatar_data_exibicao_objetos(valor, esperado) -> None:
    assert fmt.formatar_data_exibicao(valor) == esperado


@pytest.mark.regression
def test_formatar_inteiro_pt_br() -> None:
    assert fmt.formatar_inteiro_pt_br(5000) == "5.000"
    assert fmt.formatar_inteiro_pt_br(12345) == "12.345"


@pytest.mark.regression
def test_formatar_rows_para_exibicao() -> None:
    resultado = fmt.formatar_rows_para_exibicao(
        CASOS_ROWS["colunas"],
        CASOS_ROWS["rows"],
    )
    assert resultado == CASOS_ROWS["expected"]


@pytest.mark.regression
def test_dash_nao_importa_titulospub() -> None:
    dash_root = Path(__file__).resolve().parents[2] / "dash_app"
    for path in dash_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("titulospub"), (
                        f"{path} importa titulospub"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("titulospub"), (
                        f"{path} importa titulospub"
                    )
