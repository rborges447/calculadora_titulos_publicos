"""Regressao vencimentos vs golden (Spec 001, Fase 4)."""

import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import load_golden, patch_variaveis_mercado_io  # noqa: E402
from titulospub.dados.vencimentos import (  # noqa: E402
    get_codigos_di_disponiveis,
    get_todos_vencimentos,
    get_vencimentos_lft,
    get_vencimentos_ltn,
    get_vencimentos_ntnb,
    get_vencimentos_ntnf,
)


@pytest.fixture(autouse=True)
def _mock_io():
    with patch_variaveis_mercado_io():
        yield


@pytest.mark.regression
def test_get_vencimentos_ltn_igual_baseline():
    golden = load_golden("vencimentos_baseline")
    assert get_vencimentos_ltn() == golden["ltn"]


@pytest.mark.regression
def test_get_vencimentos_lft_igual_baseline():
    golden = load_golden("vencimentos_baseline")
    assert get_vencimentos_lft() == golden["lft"]


@pytest.mark.regression
def test_get_vencimentos_ntnb_igual_baseline():
    golden = load_golden("vencimentos_baseline")
    assert get_vencimentos_ntnb() == golden["ntnb"]


@pytest.mark.regression
def test_get_vencimentos_ntnf_igual_baseline():
    golden = load_golden("vencimentos_baseline")
    assert get_vencimentos_ntnf() == golden["ntnf"]


@pytest.mark.regression
def test_get_todos_vencimentos_chaves_e_tamanhos():
    golden = load_golden("vencimentos_baseline")
    todos = get_todos_vencimentos()
    assert set(todos.keys()) == {"ltn", "lft", "ntnb", "ntnf"}
    assert len(todos["ltn"]) == len(golden["ltn"])
    assert len(todos["lft"]) == len(golden["lft"])
    assert len(todos["ntnb"]) == len(golden["ntnb"])
    assert len(todos["ntnf"]) == len(golden["ntnf"])


@pytest.mark.regression
def test_get_codigos_di_count_bate_baseline():
    golden = load_golden("vencimentos_baseline")
    assert len(get_codigos_di_disponiveis()) == golden["di_codigos_count"]
