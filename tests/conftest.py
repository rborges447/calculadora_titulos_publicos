"""Suite de testes de regressão — Spec 001 (VariaveisMercado).

Esta suite congela o comportamento atual de ``VariaveisMercado`` e dos
consumidores (títulos, API) para detectar regressões antes e depois da
refatoração para lake/pacote de dados.

Fixtures de baseline: ``tests/fixtures/variaveis_mercado/``
Golden files (cálculos/API): ``tests/fixtures/golden/``

Comando principal (após Fase 3+):
    pytest tests/ -m regression -v
"""

from __future__ import annotations

import contextlib
import copy
import json
import pickle
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd
import pytest

from titulospub.dados.orquestrador import VariaveisMercado

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "variaveis_mercado"
GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"
DATA_BASE_FIXA = "2026-05-25"

CACHE_TO_FIXTURE = {
    "feriados.pkl": "feriados",
    "ipca_dict.pkl": "ipca_dict",
    "cdi.pkl": "cdi",
    "anbimas.pkl": "anbimas",
    "bmf.pkl": "bmf",
    "vna_lft.pkl": "vna_lft",
    "ptax.pkl": "ptax",
}

ANBIMAS_KEYS = {"LTN", "NTN-B", "NTN-F", "LFT"}
ANBIMAS_COLS = {"TITULO", "DATA", "VENCIMENTO", "ANBIMA", "PU", "QTD_OPERADA"}
BMF_KEYS = {"DI", "DAP"}
IPCA_KEYS = {
    "ULTIMO_MES_IPCA",
    "INDICE_IPCA_DATA_BASE",
    "INDICE_IPCA_FECHADO_ATUAL",
    "INDICE_IPCA_FECHADO_ANTERIOR",
    "VAR_IPCA_ATUAL",
    "VAR_IPCA_ANTERIOR",
    "IPCA_PROJ",
    "IPCA_USADO",
}
RTOL = 1e-9
PU_REL = 1e-9
DV01_REL = 1e-6

_NETWORK_FORBIDDEN_MSG = "rede/backup não permitido em teste de contrato"


def _forbidden_network(*args: Any, **kwargs: Any) -> None:
    raise RuntimeError(_NETWORK_FORBIDDEN_MSG)


def _mock_load_cache(filename: str) -> Any:
    fixture_name = CACHE_TO_FIXTURE.get(filename)
    if fixture_name is None:
        return None
    return load_fixture(fixture_name)


@contextmanager
def patch_variaveis_mercado_io() -> Iterator[None]:
    """Mocka I/O do orquestrador para servir baseline offline.

    Estratégia oficial (Spec 002 Fase 3): ``load_cache`` → pickles em
    ``tests/fixtures/variaveis_mercado/``; ``*_from_db`` bloqueados (sem rede/DB).
    """
    patch_targets = [
        ("titulospub.dados.orquestrador.load_cache", {"side_effect": _mock_load_cache}),
        ("titulospub.dados.orquestrador.save_cache", {}),
        (
            "titulospub.dados.orquestrador.feriados_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.ipca_dict_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.cdi_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.vna_lft_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.anbimas_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.bmf_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.ptax_from_db",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.feriados_from_scraping",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.cdi_from_scraping",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.vna_lft_from_scraping",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.anbimas_from_scraping",
            {"side_effect": _forbidden_network},
        ),
        (
            "titulospub.dados.orquestrador.bmf_from_scraping",
            {"side_effect": _forbidden_network},
        ),
    ]
    with contextlib.ExitStack() as stack:
        for target, kwargs in patch_targets:
            stack.enter_context(patch(target, **kwargs))
        yield


def load_fixture(name: str) -> Any:
    """Carrega pickle de ``tests/fixtures/variaveis_mercado/``."""
    filename = name if name.endswith(".pkl") else f"{name}.pkl"
    path = FIXTURES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Fixture não encontrada: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


def load_golden(name: str) -> dict:
    """Carrega golden JSON de ``tests/fixtures/golden/``."""
    filename = name if name.endswith(".json") else f"{name}.json"
    path = GOLDEN_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Golden não encontrado: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class VariaveisMercadoFixture:
    """Stub de ``VariaveisMercado`` que retorna dados congelados da Fase 1.

    Ignora ``force_update``, ``data`` e demais parâmetros opcionais.
    """

    def __init__(self) -> None:
        self._feriados: list | None = None
        self._ipca_dict: dict | None = None
        self._cdi: float | None = None
        self._vna_lft: float | None = None
        self._anbimas: dict[str, pd.DataFrame] | None = None
        self._bmf: dict[str, pd.DataFrame] | None = None
        self._ptax: float | None = None

    def get_feriados(self, force_update: bool = False) -> list:
        if self._feriados is None:
            self._feriados = load_fixture("feriados")
        return copy.copy(self._feriados)

    def get_ipca_dict(
        self,
        data: pd.Timestamp | None = None,
        feriados: list | None = None,
        force_update: bool = False,
    ) -> dict:
        if self._ipca_dict is None:
            self._ipca_dict = load_fixture("ipca_dict")
        return copy.copy(self._ipca_dict)

    def get_cdi(
        self,
        data: pd.Timestamp | None = None,
        force_update: bool = False,
    ) -> float:
        if self._cdi is None:
            self._cdi = load_fixture("cdi")
        return self._cdi

    def get_anbimas(
        self,
        data: pd.Timestamp | None = None,
        force_update: bool = False,
    ) -> dict[str, pd.DataFrame]:
        if self._anbimas is None:
            self._anbimas = load_fixture("anbimas")
        return {k: v.copy(deep=True) for k, v in self._anbimas.items()}

    def get_bmf(
        self,
        data: pd.Timestamp | None = None,
        force_update: bool = False,
    ) -> dict[str, pd.DataFrame]:
        if self._bmf is None:
            self._bmf = load_fixture("bmf")
        return {k: v.copy(deep=True) for k, v in self._bmf.items()}

    def get_vna_lft(
        self,
        data: pd.Timestamp | None = None,
        force_update: bool = False,
    ) -> float:
        if self._vna_lft is None:
            self._vna_lft = load_fixture("vna_lft")
        return self._vna_lft

    def get_ptax(
        self,
        data: pd.Timestamp | None = None,
        force_update: bool = False,
    ) -> float:
        if self._ptax is None:
            self._ptax = load_fixture("ptax")
        return self._ptax

    def atualizar_tudo(self, data, verbose: bool = True) -> None:
        """No-op — preparado para patch no lifespan da API (Fase 5)."""

    def limpar_cache(self) -> None:
        """No-op — preparado para patch no lifespan da API (Fase 5)."""


@pytest.fixture
def data_base_fixa() -> str:
    return DATA_BASE_FIXA


@pytest.fixture
def vm_fixo() -> VariaveisMercadoFixture:
    return VariaveisMercadoFixture()


@pytest.fixture
def vm_real() -> Iterator[VariaveisMercado]:
    """``VariaveisMercado`` real com I/O mockado para baseline offline."""
    with patch_variaveis_mercado_io():
        yield VariaveisMercado()


@pytest.fixture
def vm_offline() -> Iterator[VariaveisMercadoFixture]:
    """Stub de mercado + I/O mockado (LFT VNA, vencimentos, equivalencia)."""
    with patch_variaveis_mercado_io():
        yield VariaveisMercadoFixture()


VM_PATCH_TARGETS = [
    "titulospub.core.ltn.titulo_ltn.VariaveisMercado",
    "titulospub.core.lft.titulo_lft.VariaveisMercado",
    "titulospub.core.ntnb.titulo_ntnb.VariaveisMercado",
    "titulospub.core.ntnf.titulo_ntnf.VariaveisMercado",
    "titulospub.dados.vencimentos.VariaveisMercado",
    "api.main.VariaveisMercado",
]


@contextmanager
def patch_api_offline() -> Iterator[None]:
    """Mocka VM + I/O para requests HTTP offline (Fase 5)."""
    with patch_variaveis_mercado_io():
        with contextlib.ExitStack() as stack:
            for target in VM_PATCH_TARGETS:
                stack.enter_context(patch(target, VariaveisMercadoFixture))
            stack.enter_context(
                patch("api.main.precisa_atualizar_mercado", return_value=False)
            )
            stack.enter_context(patch("builtins.print"))
            yield


@pytest.fixture
def client() -> Iterator[Any]:
    """TestClient da API com mercado offline."""
    from starlette.testclient import TestClient

    with patch_api_offline():
        from api.main import app

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def client_data_base_fixa(client: Any) -> Iterator[Any]:
    """TestClient com ``Timestamp.today`` fixo para equivalencia."""
    with patch("pandas.Timestamp.today", return_value=pd.Timestamp(DATA_BASE_FIXA)):
        yield client
