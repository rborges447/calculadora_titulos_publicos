"""Helpers de assert para testes de regressao API."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_API_DIR = Path(__file__).resolve().parent
_TESTS_DIR = _API_DIR.parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

_ROOT_CONFTEST_PATH = _TESTS_DIR / "conftest.py"
_spec = importlib.util.spec_from_file_location("tests_root_conftest", _ROOT_CONFTEST_PATH)
_root_conftest = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_root_conftest)

load_golden = _root_conftest.load_golden
PU_REL = _root_conftest.PU_REL
DV01_REL = _root_conftest.DV01_REL

PU_FIELDS = frozenset(
    {
        "pu_d0",
        "pu_termo",
        "pu_carregado",
        "pu_ajustado",
        "cotacao",
        "taxa",
        "taxa_anbima",
        "financeiro",
        "carrego_brl",
        "carrego_bps",
        "premio",
        "di",
        "ajuste_di",
        "premio_anbima",
        "premio_anbima_dap",
        "ajuste_dap",
        "vna",
        "vna_tesouro",
        "duration",
        "equivalencia",
    }
)

DV01_FIELDS = frozenset({"dv01", "dv01_ntnb"})

INT_FIELDS = frozenset({"hedge_di", "hedge_dap", "dias_liquidacao", "dias_duration", "total"})


def assert_response_vs_golden(
    body: dict,
    expected: dict,
    *,
    skip_fields: frozenset[str] | None = None,
) -> None:
    """Compara resposta JSON da API com golden, campo a campo."""
    skip = skip_fields or frozenset()
    for key, exp_val in expected.items():
        if key in skip:
            continue
        assert key in body, f"Campo ausente na resposta: {key}"
        act_val = body[key]
        if exp_val is None:
            assert act_val is None, f"{key}: esperado None, obteve {act_val!r}"
        elif key in INT_FIELDS:
            assert act_val == exp_val, f"{key}: {act_val!r} != {exp_val!r}"
        elif key in DV01_FIELDS:
            assert act_val == pytest.approx(exp_val, rel=DV01_REL)
        elif key in PU_FIELDS and isinstance(exp_val, (int, float)):
            assert act_val == pytest.approx(exp_val, rel=PU_REL)
        else:
            assert act_val == exp_val, f"{key}: {act_val!r} != {exp_val!r}"
