"""Testes de fallback fetch_on → data anterior para séries temporais."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from titulospub.utils.datas import date_series_min, fetch_on_or_prior


@pytest.mark.regression
def test_date_series_min_usa_default(monkeypatch):
    monkeypatch.delenv("VM_DATE_SERIES_MIN", raising=False)
    assert date_series_min() == "1990-01-01"


@pytest.mark.regression
def test_date_series_min_respeita_env(monkeypatch):
    monkeypatch.setenv("VM_DATE_SERIES_MIN", "2000-01-01")
    assert date_series_min() == "2000-01-01"


@pytest.mark.regression
def test_fetch_on_or_prior_retorna_exato_quando_existe():
    reader = MagicMock()
    expected = pd.DataFrame(
        {"data_referencia": ["2026-05-25"], "cdi": [14.4]},
    )
    reader.fetch_on.return_value = expected

    result = fetch_on_or_prior(reader, "2026-05-25", variable="cdi")

    pd.testing.assert_frame_equal(result, expected)
    reader.fetch_on.assert_called_once_with("2026-05-25")
    reader.fetch_range.assert_not_called()


@pytest.mark.regression
def test_fetch_on_or_prior_usa_ultima_anterior(capsys):
    reader = MagicMock()
    reader.fetch_on.return_value = pd.DataFrame()
    reader.fetch_range.return_value = pd.DataFrame(
        {
            "data_referencia": ["2026-05-23", "2026-05-26"],
            "cdi": [14.3, 14.4],
        }
    )

    result = fetch_on_or_prior(reader, "2026-05-27", variable="cdi")

    assert len(result) == 1
    assert result["cdi"].iloc[0] == pytest.approx(14.4)
    assert pd.Timestamp(result["data_referencia"].iloc[0]).date() == pd.Timestamp(
        "2026-05-26"
    ).date()
    reader.fetch_range.assert_called_once_with("1990-01-01", "2026-05-27")
    captured = capsys.readouterr()
    assert "[AVISO] cdi: data 2026-05-27 indisponível" in captured.out
    assert "2026-05-26" in captured.out


@pytest.mark.regression
def test_fetch_on_or_prior_respeita_vm_date_series_min(monkeypatch):
    monkeypatch.setenv("VM_DATE_SERIES_MIN", "2000-01-01")
    reader = MagicMock()
    reader.fetch_on.return_value = pd.DataFrame()
    reader.fetch_range.return_value = pd.DataFrame(
        {"data_referencia": ["2026-05-26"], "cdi": [14.4]},
    )

    fetch_on_or_prior(reader, "2026-05-27", variable="cdi")

    reader.fetch_range.assert_called_once_with("2000-01-01", "2026-05-27")


@pytest.mark.regression
def test_fetch_on_or_prior_levanta_sem_historico():
    reader = MagicMock()
    reader.fetch_on.return_value = pd.DataFrame()
    reader.fetch_range.return_value = pd.DataFrame()

    with pytest.raises(ValueError, match="sem dados no banco"):
        fetch_on_or_prior(reader, "2026-05-27", variable="cdi")


@pytest.mark.regression
def test_cdi_from_db_fallback_para_data_anterior():
    from titulospub.dados.transforms.cdi import cdi_from_db

    reader = MagicMock()
    reader.cdi.fetch_on.return_value = pd.DataFrame()
    reader.cdi.fetch_range.return_value = pd.DataFrame(
        {"data_referencia": ["2026-05-26"], "cdi": [14.4]},
    )

    with patch(
        "titulospub.dados.db_reader.get_reader",
        return_value=reader,
    ):
        assert cdi_from_db("2026-05-27") == pytest.approx(14.4)


@pytest.mark.regression
def test_ptax_from_db_fallback_para_data_anterior():
    from titulospub.dados.transforms.ptax import ptax_from_db

    reader = MagicMock()
    reader.ptax.fetch_on.return_value = pd.DataFrame()
    reader.ptax.fetch_range.return_value = pd.DataFrame(
        {"data_referencia": ["2026-05-26"], "ptax_venda": [5.0072]},
    )

    with patch(
        "titulospub.dados.db_reader.get_reader",
        return_value=reader,
    ):
        assert ptax_from_db("2026-05-27") == pytest.approx(5.0072)
