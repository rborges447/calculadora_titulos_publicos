"""Validacao 422 nos routers POST (Spec 001, Fase 5)."""

import pytest


@pytest.mark.regression
@pytest.mark.parametrize(
    "path",
    [
        "/titulos/ltn",
        "/titulos/lft",
        "/titulos/ntnb",
        "/titulos/ntnf",
    ],
)
def test_post_titulo_body_vazio_retorna_422(client, path):
    resp = client.post(path, json={})
    assert resp.status_code == 422


@pytest.mark.regression
def test_post_equivalencia_criterio_invalido_retorna_422(client_data_base_fixa):
    payload = {
        "titulo1": "LTN",
        "venc1": "2027-07-01",
        "titulo2": "NTNF",
        "venc2": "2029-01-01",
        "qtd1": 50000,
        "tx1": 12.5,
        "tx2": 12.5,
        "criterio": "invalido",
    }
    resp = client_data_base_fixa.post("/equivalencia", json=payload)
    assert resp.status_code == 422
