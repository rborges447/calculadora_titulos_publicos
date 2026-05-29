"""Regressao LFT vs golden (Spec 001, Fase 4)."""

import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import PU_REL, load_golden  # noqa: E402
from titulospub.core import LFT  # noqa: E402


def _build_lft_from_golden(golden: dict, vm) -> LFT:
    return LFT(
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
def test_lft_pu_d0_bate_golden(vm_offline):
    golden = load_golden("lft_2027_taxa_0_01")
    lft = _build_lft_from_golden(golden, vm_offline)
    assert lft.pu_d0 == pytest.approx(golden["outputs"]["pu_d0"], rel=PU_REL)


@pytest.mark.regression
def test_lft_cotacao_e_pu_termo_batem_golden(vm_offline):
    golden = load_golden("lft_2027_taxa_0_01")
    lft = _build_lft_from_golden(golden, vm_offline)
    out = golden["outputs"]
    assert lft.cotacap == pytest.approx(out["cotacao"], rel=PU_REL)
    assert lft.pu_termo == pytest.approx(out["pu_termo"], rel=PU_REL)
    assert lft.pu_carregado == pytest.approx(out["pu_carregado"], rel=PU_REL)
    assert lft.financeiro == pytest.approx(out["financeiro"], rel=PU_REL)
