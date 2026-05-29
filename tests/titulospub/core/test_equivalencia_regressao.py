"""Regressao equivalencia vs golden (Spec 001, Fase 4)."""

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import DV01_REL, load_golden, patch_variaveis_mercado_io  # noqa: E402
from titulospub.core.equivalencia import equivalencia  # noqa: E402


@pytest.mark.regression
def test_equivalencia_ltn_ntnf_dv_bate_golden():
    golden = load_golden("equivalencia_ltn_ntnf_dv")
    fixed_today = pd.Timestamp(golden["data_base"])

    with patch_variaveis_mercado_io(), patch(
        "pandas.Timestamp.today", return_value=fixed_today
    ):
        resultado = equivalencia(
            titulo1=golden["titulo1"],
            venc1=golden["venc1"],
            titulo2=golden["titulo2"],
            venc2=golden["venc2"],
            qtd1=golden["qtd1"],
            tx1=golden["tx1"],
            tx2=golden["tx2"],
            criterio=golden["criterio"],
        )

    assert resultado == pytest.approx(golden["resultado"], rel=DV01_REL)
