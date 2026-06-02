"""Contrato de paridade domínio ↔ Dash para formatação pt-BR (Spec 004, T-010)."""

from __future__ import annotations

import pytest

from dash_app.utils.formatacao_pt_br import formatar_numero_pt_br as dash_numero
from tests.fixtures.formatacao_pt_br_casos import CASOS_NUMERO
from titulospub.dados.consultas_db.formatacao import formatar_numero_pt_br as dom_numero


@pytest.mark.regression
@pytest.mark.parametrize(("valor", "casas", "esperado"), CASOS_NUMERO)
def test_paridade_formatar_numero_pt_br(valor, casas, esperado) -> None:
    if casas is None:
        assert dom_numero(valor) == dash_numero(valor) == esperado
    else:
        assert dom_numero(valor, casas_decimais=casas) == dash_numero(
            valor, casas_decimais=casas
        ) == esperado
