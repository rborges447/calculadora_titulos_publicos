"""Testes do preview interativo da página Consultas DB (Spec 004, Fase 3)."""

from __future__ import annotations

import pytest

from dash_app.pages.consultas_db import (
    _build_payload,
    _colunas_ocultas,
    _format_date,
    _intervalo_padrao_fonte,
)


@pytest.mark.regression
def test_colunas_ocultas() -> None:
    assert _colunas_ocultas(["a", "b", "c"], ["a", "c"]) == ["b"]


@pytest.mark.regression
def test_colunas_ocultas_todas_visiveis() -> None:
    assert _colunas_ocultas(["a", "b"], ["a", "b"]) == []


@pytest.mark.regression
def test_colunas_ocultas_uma_visivel() -> None:
    assert _colunas_ocultas(["a", "b", "c"], ["b"]) == ["a", "c"]


@pytest.mark.regression
def test_format_date_iso_e_timestamp() -> None:
    assert _format_date("2026-05-29") == "2026-05-29"
    assert _format_date("01/06/2026") == "2026-06-01"
    ts_ms = 1_749_916_800_000  # 2025-06-14 UTC approx — só verifica formato
    assert _format_date(ts_ms) is not None
    assert len(_format_date(ts_ms)) == 10


@pytest.mark.regression
def test_intervalo_padrao_fonte_ultimos_30_dias() -> None:
    ini, fim = _intervalo_padrao_fonte("2026-01-02", "2026-05-29")
    assert fim == "2026-05-29"
    assert ini == "2026-04-29"


@pytest.mark.regression
def test_build_payload_range_sem_datas_mensagem_disponivel() -> None:
    fonte = {
        "id": "mercado_secundario",
        "modo": "range",
        "data_disponivel_inicio": "2026-01-02",
        "data_disponivel_fim": "2026-05-29",
    }
    payload, erro = _build_payload(
        "mercado_secundario",
        ["data_referencia"],
        None,
        None,
        fonte,
    )
    assert payload is None
    assert erro is not None
    assert "2026-01-02" in erro or "02/01/2026" in erro
    assert "05/29/2026" in erro or "29/05/2026" in erro


@pytest.mark.regression
def test_build_payload_range_com_datas() -> None:
    fonte = {"id": "cdi", "modo": "range"}
    payload, erro = _build_payload(
        "cdi",
        ["data_referencia", "cdi"],
        "2026-01-02",
        "2026-01-10",
        fonte,
    )
    assert erro is None
    assert payload["data_inicio"] == "2026-01-02"
    assert payload["data_fim"] == "2026-01-10"
