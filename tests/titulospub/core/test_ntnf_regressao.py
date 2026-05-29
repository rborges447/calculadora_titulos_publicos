"""Regressao NTN-F vs golden (Spec 001, Fase 4)."""

import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import DV01_REL, PU_REL, load_golden  # noqa: E402
from titulospub.core import NTNF  # noqa: E402


def _build_ntnf_from_golden(golden: dict, vm) -> NTNF:
    return NTNF(
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
def test_ntnf_pu_d0_bate_golden(vm_offline):
    golden = load_golden("ntnf_2029_taxa_12_5")
    ntnf = _build_ntnf_from_golden(golden, vm_offline)
    assert ntnf.pu_d0 == pytest.approx(golden["outputs"]["pu_d0"], rel=PU_REL)


@pytest.mark.regression
def test_ntnf_dv01_bate_golden(vm_offline):
    golden = load_golden("ntnf_2029_taxa_12_5")
    ntnf = _build_ntnf_from_golden(golden, vm_offline)
    assert ntnf.dv01 == pytest.approx(golden["outputs"]["dv01"], rel=DV01_REL)


@pytest.mark.regression
def test_ntnf_hedge_di_e_financeiro_batem_golden(vm_offline):
    golden = load_golden("ntnf_2029_taxa_12_5")
    ntnf = _build_ntnf_from_golden(golden, vm_offline)
    out = golden["outputs"]
    assert ntnf.hedge_di == pytest.approx(out["hedge_di"], rel=DV01_REL)
    assert ntnf.financeiro == pytest.approx(out["financeiro"], rel=PU_REL)
