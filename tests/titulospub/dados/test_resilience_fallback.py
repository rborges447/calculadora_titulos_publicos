"""Testes de fallback DB → scraping (opt-in, sem rede na regressão)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

_TESTS_DIR = Path(__file__).resolve().parents[2]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from titulospub.dados.resilience import fetch_with_fallback


@pytest.mark.regression
def test_fetch_with_fallback_raises_without_flag(monkeypatch):
    monkeypatch.delenv("VM_ALLOW_SCRAPING_FALLBACK", raising=False)

    def from_db():
        raise FileNotFoundError("db ausente")

    def from_scraping():
        return 42.0

    with pytest.raises(FileNotFoundError):
        fetch_with_fallback("cdi", from_db, from_scraping)


@pytest.mark.regression
def test_fetch_with_fallback_uses_scrape_when_enabled(monkeypatch):
    monkeypatch.setenv("VM_ALLOW_SCRAPING_FALLBACK", "1")

    def from_db():
        raise FileNotFoundError("db ausente")

    def from_scraping():
        return 14.4

    assert fetch_with_fallback("cdi", from_db, from_scraping) == pytest.approx(14.4)


@pytest.mark.slow
def test_get_cdi_fallback_integration(monkeypatch):
    """Com DB mockado como ausente, CDI vem do scrape (rede)."""
    monkeypatch.setenv("VM_ALLOW_SCRAPING_FALLBACK", "1")

    from titulospub.dados.orquestrador import VariaveisMercado
    from titulospub.dados.transforms import cdi as cdi_mod

    def _fail_db(data):
        raise FileNotFoundError("simulado")

    monkeypatch.setattr(cdi_mod, "cdi_from_db", _fail_db)

    vm = VariaveisMercado()
    data = pd.Timestamp("2026-05-25")
    value = vm.get_cdi(data=data, force_update=True)
    assert isinstance(value, float)
