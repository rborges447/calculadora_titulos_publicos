"""Regressao GET /vencimentos vs golden (Spec 001, Fase 5)."""

import sys
from pathlib import Path

import pytest

_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from helpers import load_golden  # noqa: E402


@pytest.mark.regression
def test_get_vencimentos_ltn(client):
    golden = load_golden("vencimentos_baseline")
    resp = client.get("/vencimentos/ltn")
    assert resp.status_code == 200
    assert resp.json() == golden["ltn"]


@pytest.mark.regression
def test_get_vencimentos_lft(client):
    golden = load_golden("vencimentos_baseline")
    resp = client.get("/vencimentos/lft")
    assert resp.status_code == 200
    assert resp.json() == golden["lft"]


@pytest.mark.regression
def test_get_vencimentos_ntnb(client):
    golden = load_golden("vencimentos_baseline")
    resp = client.get("/vencimentos/ntnb")
    assert resp.status_code == 200
    assert resp.json() == golden["ntnb"]


@pytest.mark.regression
def test_get_vencimentos_ntnf(client):
    golden = load_golden("vencimentos_baseline")
    resp = client.get("/vencimentos/ntnf")
    assert resp.status_code == 200
    assert resp.json() == golden["ntnf"]


@pytest.mark.regression
def test_get_vencimentos_todos_detalhes(client):
    golden = load_golden("vencimentos_baseline")
    resp = client.get("/vencimentos/todos/detalhes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ltn"] == golden["ltn"]
    assert body["lft"] == golden["lft"]
    assert body["ntnb"] == golden["ntnb"]
    assert body["ntnf"] == golden["ntnf"]


@pytest.mark.regression
def test_get_codigos_di_detalhes(client):
    golden = load_golden("vencimentos_baseline")
    resp = client.get("/vencimentos/di/detalhes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == golden["di_codigos_count"]
    assert len(body["codigos"]) == golden["di_codigos_count"]
