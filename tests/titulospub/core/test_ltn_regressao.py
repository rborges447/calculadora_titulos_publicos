"""Regressao LTN vs golden (Spec 001, Fase 4)."""

import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import DV01_REL, PU_REL, load_golden  # noqa: E402
from titulospub.core import LTN  # noqa: E402


def _build_ltn_from_golden(golden: dict, vm) -> LTN:
    return LTN(
        data_vencimento_titulo=golden["data_vencimento"],
        data_base=golden["data_base"],
        taxa=golden["taxa"],
        quantidade=golden["quantidade"],
        dias_liquidacao=golden.get("dias_liquidacao", 1),
        variaveis_mercado=vm,
        feriados=vm.get_feriados(),
        cdi=vm.get_cdi(),
    )


@pytest.mark.regression
def test_ltn_pu_d0_bate_golden(vm_offline):
    golden = load_golden("ltn_2027_taxa_12_5")
    ltn = _build_ltn_from_golden(golden, vm_offline)
    assert ltn.pu_d0 == pytest.approx(golden["outputs"]["pu_d0"], rel=PU_REL)


@pytest.mark.regression
def test_ltn_dv01_bate_golden(vm_offline):
    golden = load_golden("ltn_2027_taxa_12_5")
    ltn = _build_ltn_from_golden(golden, vm_offline)
    assert ltn.dv01 == pytest.approx(golden["outputs"]["dv01"], rel=DV01_REL)


@pytest.mark.regression
def test_ltn_hedge_di_bate_golden(vm_offline):
    golden = load_golden("ltn_2027_taxa_12_5")
    ltn = _build_ltn_from_golden(golden, vm_offline)
    assert ltn.hedge_di == golden["outputs"]["hedge_di"]


@pytest.mark.regression
def test_ltn_outputs_financeiros_batem_golden(vm_offline):
    golden = load_golden("ltn_2027_taxa_12_5")
    ltn = _build_ltn_from_golden(golden, vm_offline)
    out = golden["outputs"]
    assert ltn.pu_termo == pytest.approx(out["pu_termo"], rel=PU_REL)
    assert ltn.pu_carregado == pytest.approx(out["pu_carregado"], rel=PU_REL)
    assert ltn.financeiro == pytest.approx(out["financeiro"], rel=PU_REL)
    assert ltn.carrego_brl == pytest.approx(out["carrego_brl"], rel=DV01_REL)
