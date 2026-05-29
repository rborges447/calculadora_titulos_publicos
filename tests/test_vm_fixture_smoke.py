"""Smoke tests do stub VariaveisMercadoFixture (Fase 2)."""

import pytest

pytestmark = pytest.mark.regression


def test_vm_fixo_carrega_feriados(vm_fixo):
    feriados = vm_fixo.get_feriados()
    assert isinstance(feriados, list)
    assert len(feriados) == 1263


def test_vm_fixo_cdi_bate_baseline(vm_fixo):
    assert vm_fixo.get_cdi() == pytest.approx(14.4)


def test_vm_fixo_anbimas_tem_chaves_obrigatorias(vm_fixo):
    anbimas = vm_fixo.get_anbimas()
    assert {"LTN", "NTN-B", "NTN-F", "LFT"}.issubset(anbimas.keys())


def test_vm_fixo_bmf_tem_di_e_dap(vm_fixo):
    bmf = vm_fixo.get_bmf()
    assert {"DI", "DAP"}.issubset(bmf.keys())
    assert len(bmf["DI"]) > 0
    assert len(bmf["DAP"]) > 0


def test_vm_fixo_vna_lft_bate_baseline(vm_fixo):
    assert vm_fixo.get_vna_lft() == pytest.approx(19069.075129)


def test_vm_fixo_anbimas_retorna_copia_independente(vm_fixo):
    anbimas_a = vm_fixo.get_anbimas()
    anbimas_b = vm_fixo.get_anbimas()
    anbimas_a["LTN"].iloc[0, anbimas_a["LTN"].columns.get_loc("ANBIMA")] = -999.0
    assert anbimas_b["LTN"].iloc[0]["ANBIMA"] != -999.0


def test_data_base_fixa(data_base_fixa):
    assert data_base_fixa == "2026-05-25"
