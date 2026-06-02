"""Testes de formatação pt-BR para consultas_db (Spec 004, T-001)."""

from __future__ import annotations

import pandas as pd
import pytest

from tests.fixtures.formatacao_pt_br_casos import (
    CASOS_DATA_OBJETOS,
    CASOS_DATA_STRING,
    CASOS_NUMERO,
)
from titulospub.dados.consultas_db.formatacao import (
    CSV_SEPARADOR_CAMPOS,
    formatar_data_exibicao,
    formatar_dataframe_para_csv_pt_br,
    formatar_numero_pt_br,
)


@pytest.mark.parametrize(("valor", "casas", "esperado"), CASOS_NUMERO)
def test_formatar_numero_pt_br(valor, casas, esperado) -> None:
    if casas is None:
        assert formatar_numero_pt_br(valor) == esperado
    else:
        assert formatar_numero_pt_br(valor, casas_decimais=casas) == esperado


@pytest.mark.parametrize(("valor", "esperado"), CASOS_DATA_STRING)
def test_formatar_data_exibicao_string(valor, esperado) -> None:
    assert formatar_data_exibicao(valor) == esperado


@pytest.mark.parametrize(("valor", "esperado"), CASOS_DATA_OBJETOS)
def test_formatar_data_exibicao_objetos(valor, esperado) -> None:
    assert formatar_data_exibicao(valor) == esperado


def test_formatar_dataframe_para_csv_pt_br_misto() -> None:
    df = pd.DataFrame(
        {
            "data_referencia": pd.to_datetime(["2024-01-01"]),
            "cdi": [0.123456],
            "tipo_titulo": ["LTN"],
            "qtd_operacoes": [1500],
        }
    )
    resultado = formatar_dataframe_para_csv_pt_br(df)

    assert resultado.iloc[0]["data_referencia"] == "01/01/2024"
    assert resultado.iloc[0]["cdi"] == "0,123456"
    assert resultado.iloc[0]["tipo_titulo"] == "LTN"
    assert resultado.iloc[0]["qtd_operacoes"] == "1.500"


def test_csv_separador_constante() -> None:
    assert CSV_SEPARADOR_CAMPOS == ";"
