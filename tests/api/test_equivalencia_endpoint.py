"""Regressao POST /equivalencia vs golden (Spec 001, Fase 5)."""

import sys
from pathlib import Path

import pytest

_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from helpers import DV01_REL, assert_response_vs_golden, load_golden  # noqa: E402


@pytest.mark.regression
def test_post_equivalencia_ltn_ntnf_dv_bate_golden(client_data_base_fixa):
    golden = load_golden("api_equivalencia_ltn_ntnf_dv")
    resp = client_data_base_fixa.post("/equivalencia", json=golden["request"])
    assert resp.status_code == 200
    body = resp.json()
    assert_response_vs_golden(body, golden["response"])

    core = load_golden("equivalencia_ltn_ntnf_dv")
    assert body["equivalencia"] == pytest.approx(core["resultado"], rel=DV01_REL)
