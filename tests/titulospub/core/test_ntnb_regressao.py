"""Regressao NTN-B vs golden (Spec 001, Fase 4)."""

import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import DV01_REL, PU_REL, load_golden  # noqa: E402
from titulospub.core import NTNB  # noqa: E402


def _build_ntnb_from_golden(golden: dict, vm) -> NTNB:
    return NTNB(
        data_vencimento_titulo=golden["data_vencimento"],
        data_base=golden["data_base"],
        taxa=golden["taxa"],
        quantidade=golden["quantidade"],
        dias_liquidacao=golden.get("dias_liquidacao", 1),
        variaveis_mercado=vm,
        feriados=vm.get_feriados(),
        cdi=vm.get_cdi(),
        ipca_dict=vm.get_ipca_dict(),
    )


@pytest.mark.regression
def test_ntnb_pu_d0_bate_golden(vm_offline):
    golden = load_golden("ntnb_2035_taxa_7_0")
    ntnb = _build_ntnb_from_golden(golden, vm_offline)
    assert ntnb.pu_d0 == pytest.approx(golden["outputs"]["pu_d0"], rel=PU_REL)


@pytest.mark.regression
def test_ntnb_dv01_bate_golden(vm_offline):
    golden = load_golden("ntnb_2035_taxa_7_0")
    ntnb = _build_ntnb_from_golden(golden, vm_offline)
    assert ntnb.dv01 == pytest.approx(golden["outputs"]["dv01"], rel=DV01_REL)


@pytest.mark.regression
def test_ntnb_cotacao_e_duration_batem_golden(vm_offline):
    golden = load_golden("ntnb_2035_taxa_7_0")
    ntnb = _build_ntnb_from_golden(golden, vm_offline)
    out = golden["outputs"]
    assert ntnb.cotacao == pytest.approx(out["cotacao"], rel=PU_REL)
    assert ntnb.duration == pytest.approx(out["duration"], rel=PU_REL)
    assert ntnb.carrego_brl == pytest.approx(out["carrego_brl"], rel=DV01_REL)


@pytest.mark.regression
def test_ntnb_hedge_dap_bate_golden_se_disponivel(vm_offline):
    golden = load_golden("ntnb_2035_taxa_7_0")
    ntnb = _build_ntnb_from_golden(golden, vm_offline)
    expected = golden["outputs"].get("hedge_dap")
    if expected is None:
        pytest.skip("hedge_dap ausente no golden")
    assert ntnb.hedge_dap == expected
