"""Regressao POST /titulos/ltn vs golden (Spec 001, Fase 5)."""

import sys
from pathlib import Path

import pytest

_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from helpers import PU_REL, assert_response_vs_golden, load_golden  # noqa: E402


@pytest.mark.regression
def test_post_ltn_bate_golden(client):
    golden = load_golden("api_ltn_response")
    resp = client.post("/titulos/ltn", json=golden["request"])
    assert resp.status_code == 200
    body = resp.json()
    assert_response_vs_golden(body, golden["response"])

    core = load_golden("ltn_2027_taxa_12_5")
    assert body["pu_d0"] == pytest.approx(core["outputs"]["pu_d0"], rel=PU_REL)
    assert body["dv01"] == pytest.approx(core["outputs"]["dv01"], rel=1e-6)
    assert body["hedge_di"] == core["outputs"]["hedge_di"]
