"""Regressao POST /titulos/lft vs golden (Spec 001, Fase 5)."""

import sys
from pathlib import Path

import pytest

_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from helpers import PU_REL, assert_response_vs_golden, load_golden  # noqa: E402


@pytest.mark.regression
def test_post_lft_bate_golden(client):
    golden = load_golden("api_lft_response")
    resp = client.post("/titulos/lft", json=golden["request"])
    assert resp.status_code == 200
    body = resp.json()
    assert_response_vs_golden(body, golden["response"], skip_fields=frozenset({"dv01"}))

    core = load_golden("lft_2027_taxa_0_01")
    assert body["pu_d0"] == pytest.approx(core["outputs"]["pu_d0"], rel=PU_REL)
    assert body["pu_termo"] == pytest.approx(core["outputs"]["pu_termo"], rel=PU_REL)
    assert body["cotacao"] == pytest.approx(core["outputs"]["cotacao"], rel=PU_REL)
