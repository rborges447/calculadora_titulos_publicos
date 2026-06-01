"""Regra de data de leitura ANBIMA/BMF: literal, exceto se for hoje → D-1 útil."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from titulospub.dados.orquestrador import VariaveisMercado

DATA_PASSADA = pd.Timestamp("2026-05-25")
HOJE_FIXO = pd.Timestamp("2026-05-29")
D_MENOS_1 = pd.Timestamp("2026-05-28")


@pytest.mark.regression
def test_get_anbimas_data_passada_usa_literal_no_adapter():
    capturada: list[str] = []

    def _fake_anbimas_from_db(data):
        capturada.append(pd.Timestamp(data).strftime("%Y-%m-%d"))
        return {"LTN": pd.DataFrame()}

    vm = VariaveisMercado()
    with patch(
        "titulospub.dados.orquestrador.anbimas_from_db",
        side_effect=_fake_anbimas_from_db,
    ):
        with patch("titulospub.dados.orquestrador.save_cache"):
            with patch(
                "pandas.Timestamp.today",
                return_value=HOJE_FIXO,
            ):
                vm.get_anbimas(data=DATA_PASSADA, force_update=True)

    assert capturada == ["2026-05-25"]


@pytest.mark.regression
def test_get_anbimas_hoje_usa_d_menos_1_no_adapter():
    capturada: list[str] = []

    def _fake_anbimas_from_db(data):
        capturada.append(pd.Timestamp(data).strftime("%Y-%m-%d"))
        return {"LTN": pd.DataFrame()}

    vm = VariaveisMercado()
    with patch(
        "titulospub.dados.orquestrador.anbimas_from_db",
        side_effect=_fake_anbimas_from_db,
    ):
        with patch("titulospub.dados.orquestrador.save_cache"):
            with patch(
                "pandas.Timestamp.today",
                return_value=HOJE_FIXO,
            ):
                vm.get_anbimas(data=HOJE_FIXO, force_update=True)

    assert capturada == [D_MENOS_1.strftime("%Y-%m-%d")]
