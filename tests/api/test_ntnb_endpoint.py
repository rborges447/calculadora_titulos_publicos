"""Regressao POST /titulos/ntnb vs golden (Spec 001, Fase 5)."""

import sys
from pathlib import Path

import pytest

_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from helpers import PU_REL, assert_response_vs_golden, load_golden  # noqa: E402


@pytest.mark.regression
def test_post_ntnb_bate_golden(client):
    golden = load_golden("api_ntnb_response")
    resp = client.post("/titulos/ntnb", json=golden["request"])
    assert resp.status_code == 200
    body = resp.json()
    assert_response_vs_golden(body, golden["response"])

    core = load_golden("ntnb_2035_taxa_7_0")
    assert body["pu_d0"] == pytest.approx(core["outputs"]["pu_d0"], rel=PU_REL)
    assert body["dv01"] == pytest.approx(core["outputs"]["dv01"], rel=1e-6)
    assert body["cotacao"] == pytest.approx(core["outputs"]["cotacao"], rel=PU_REL)
    assert body["duration"] == pytest.approx(core["outputs"]["duration"], rel=PU_REL)
    if core["outputs"].get("hedge_dap") is not None:
        assert body["hedge_dap"] == core["outputs"]["hedge_dap"]
