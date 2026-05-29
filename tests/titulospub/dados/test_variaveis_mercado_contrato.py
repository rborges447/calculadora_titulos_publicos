"""Camada 1 — testes de contrato de VariaveisMercado (Spec 001, Fase 3)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import (  # noqa: E402
    ANBIMAS_COLS,
    ANBIMAS_KEYS,
    BMF_KEYS,
    DATA_BASE_FIXA,
    IPCA_KEYS,
    RTOL,
    load_fixture,
)

DATA_BASE = pd.Timestamp(DATA_BASE_FIXA)


@pytest.mark.regression
def test_get_feriados_retorna_lista_com_tamanho_esperado(vm_real):
    feriados = vm_real.get_feriados()
    assert isinstance(feriados, list)
    assert len(feriados) == 1263


@pytest.mark.regression
def test_get_cdi_retorna_float_igual_baseline(vm_real):
    assert vm_real.get_cdi() == pytest.approx(14.4)


@pytest.mark.regression
def test_get_ipca_dict_chaves_e_tipos(vm_real):
    feriados = load_fixture("feriados")
    ipca_dict = vm_real.get_ipca_dict(data=DATA_BASE, feriados=feriados)

    assert set(ipca_dict.keys()) == IPCA_KEYS
    assert isinstance(ipca_dict["ULTIMO_MES_IPCA"], int)
    assert isinstance(ipca_dict["INDICE_IPCA_DATA_BASE"], float)
    assert isinstance(ipca_dict["INDICE_IPCA_FECHADO_ATUAL"], float)
    assert isinstance(ipca_dict["INDICE_IPCA_FECHADO_ANTERIOR"], float)
    assert isinstance(ipca_dict["VAR_IPCA_ATUAL"], float)
    assert isinstance(ipca_dict["VAR_IPCA_ANTERIOR"], float)
    assert isinstance(ipca_dict["IPCA_PROJ"], float)
    assert isinstance(ipca_dict["IPCA_USADO"], float)


@pytest.mark.regression
def test_get_anbimas_chaves_e_colunas(vm_real):
    anbimas = vm_real.get_anbimas(data=DATA_BASE)

    assert ANBIMAS_KEYS.issubset(anbimas.keys())
    for titulo in ANBIMAS_KEYS:
        df = anbimas[titulo]
        assert ANBIMAS_COLS.issubset(set(df.columns))
        assert pd.api.types.is_datetime64_any_dtype(df["DATA"])
        assert pd.api.types.is_datetime64_any_dtype(df["VENCIMENTO"])
        assert pd.api.types.is_numeric_dtype(df["ANBIMA"])
        assert pd.api.types.is_numeric_dtype(df["PU"])


@pytest.mark.regression
def test_get_anbimas_dataframes_iguais_baseline(vm_real):
    expected = load_fixture("anbimas")
    actual = vm_real.get_anbimas(data=DATA_BASE)

    for titulo in ANBIMAS_KEYS:
        pd.testing.assert_frame_equal(
            actual[titulo],
            expected[titulo],
            check_exact=False,
            rtol=RTOL,
        )


@pytest.mark.regression
def test_get_bmf_chaves_di_dap_e_colunas(vm_real):
    bmf = vm_real.get_bmf(data=DATA_BASE)

    assert BMF_KEYS.issubset(bmf.keys())
    for nome in BMF_KEYS:
        df = bmf[nome]
        expected_cols = {"DATA", "DATA_VENCIMENTO", nome, "ADJ"}
        assert expected_cols.issubset(set(df.columns))
        assert pd.api.types.is_datetime64_any_dtype(df["DATA"])
        assert pd.api.types.is_datetime64_any_dtype(df["DATA_VENCIMENTO"])
        assert pd.api.types.is_numeric_dtype(df["ADJ"])
        assert df["DATA_VENCIMENTO"].is_monotonic_increasing


@pytest.mark.regression
def test_get_bmf_dataframes_iguais_baseline(vm_real):
    expected = load_fixture("bmf")
    actual = vm_real.get_bmf(data=DATA_BASE)

    for nome in BMF_KEYS:
        pd.testing.assert_frame_equal(
            actual[nome],
            expected[nome],
            check_exact=False,
            rtol=RTOL,
        )


@pytest.mark.regression
def test_get_vna_lft_retorna_float_igual_baseline(vm_real):
    vna_lft = vm_real.get_vna_lft(data=DATA_BASE)
    assert isinstance(vna_lft, float)
    assert vna_lft == pytest.approx(19069.075129)


@pytest.mark.regression
def test_get_cdi_force_update_sem_data_levanta(vm_real):
    with pytest.raises(ValueError, match="data"):
        vm_real.get_cdi(force_update=True)


@pytest.mark.skip(reason="Adapter lake ainda não implementado — Spec Fase 7")
@pytest.mark.regression
def test_get_bmf_via_lake_adapter_igual_baseline():
    """Placeholder T-027: validar adapter lake quando refatoração existir."""
