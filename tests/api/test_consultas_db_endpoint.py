"""Testes dos endpoints /consultas-db (Spec 003, Fase 2) com mock do domínio."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from titulospub.dados.consultas_db import (
    BancoIndisponivelError,
    ColunasInvalidasError,
    ConsultaResultado,
    IntervaloSemDadosError,
    LimiteExportacaoError,
    TabelaDesconhecidaError,
)

_FONTE_FAKE = {
    "id": "cdi",
    "rotulo": "CDI",
    "reader_attr": "cdi",
    "modo": "range",
    "coluna_data": "data_referencia",
    "colunas": ["data_referencia", "cdi"],
    "colunas_padrao": ["data_referencia", "cdi"],
    "descricao": "Taxa CDI diária",
}

_PAYLOAD_OK = {
    "tabela": "cdi",
    "colunas": ["data_referencia", "cdi"],
    "data_inicio": "2024-01-01",
    "data_fim": "2024-01-31",
}

_RESULTADO_FAKE = ConsultaResultado(
    tabela="cdi",
    data_inicio="2024-01-01",
    data_fim="2024-01-31",
    colunas=["data_referencia", "cdi"],
    total_linhas=2,
    truncado=False,
    rows=[
        {"data_referencia": "2024-01-01", "cdi": 0.12},
        {"data_referencia": "2024-01-02", "cdi": 0.13},
    ],
)


@pytest.mark.regression
@patch("api.routers.consultas_db.listar_catalogo", return_value=[_FONTE_FAKE])
def test_get_catalogo_ok(mock_listar, client):
    resp = client.get("/consultas-db/catalogo")
    assert resp.status_code == 200
    data = resp.json()
    assert "fontes" in data
    assert len(data["fontes"]) == 1
    assert data["fontes"][0]["id"] == "cdi"
    mock_listar.assert_called_once()


@pytest.mark.regression
@patch("api.routers.consultas_db.listar_catalogo", return_value=[_FONTE_FAKE])
@patch("api.routers.consultas_db.get_db_path")
def test_get_status_ok(mock_get_db_path, mock_listar, client, tmp_path):
    db_file = tmp_path / "app.db"
    db_file.write_bytes(b"sqlite")
    mock_get_db_path.return_value = db_file

    resp = client.get("/consultas-db/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["db_existe"] is True
    assert data["db_path"] == str(db_file)
    assert data["total_fontes"] == 1


@pytest.mark.regression
@patch("api.routers.consultas_db.consultar", return_value=_RESULTADO_FAKE)
def test_post_consultar_ok(mock_consultar, client):
    resp = client.post("/consultas-db/consultar", json=_PAYLOAD_OK)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tabela"] == "cdi"
    assert data["total_linhas"] == 2
    assert data["truncado"] is False
    assert len(data["rows"]) == 2
    mock_consultar.assert_called_once_with(**_PAYLOAD_OK)


@pytest.mark.regression
@patch(
    "api.routers.consultas_db.consultar",
    side_effect=TabelaDesconhecidaError("inexistente"),
)
def test_post_consultar_tabela_desconhecida(mock_consultar, client):
    resp = client.post("/consultas-db/consultar", json=_PAYLOAD_OK)
    assert resp.status_code == 404
    assert "inexistente" in resp.json()["detail"]
    mock_consultar.assert_called_once()


@pytest.mark.regression
@patch(
    "api.routers.consultas_db.consultar",
    side_effect=IntervaloSemDadosError(
        "cdi",
        pedido_inicio="2025-01-01",
        pedido_fim="2025-12-31",
        disponivel_inicio="2024-01-01",
        disponivel_fim="2024-06-30",
    ),
)
def test_post_consultar_intervalo_sem_dados(mock_consultar, client):
    resp = client.post("/consultas-db/consultar", json=_PAYLOAD_OK)
    assert resp.status_code == 422
    assert "2024-01-01" in resp.json()["detail"]
    mock_consultar.assert_called_once()


@pytest.mark.regression
@patch(
    "api.routers.consultas_db.consultar",
    side_effect=ColunasInvalidasError("cdi", colunas_invalidas=["foo"]),
)
def test_post_consultar_colunas_invalidas(mock_consultar, client):
    resp = client.post("/consultas-db/consultar", json=_PAYLOAD_OK)
    assert resp.status_code == 422
    mock_consultar.assert_called_once()


@pytest.mark.regression
@patch(
    "api.routers.consultas_db.consultar",
    side_effect=BancoIndisponivelError("/tmp/missing.db"),
)
def test_post_consultar_banco_indisponivel(mock_consultar, client):
    resp = client.post("/consultas-db/consultar", json=_PAYLOAD_OK)
    assert resp.status_code == 503
    mock_consultar.assert_called_once()


@pytest.mark.regression
@patch(
    "api.routers.consultas_db.exportar_csv",
    return_value=(b"data_referencia,cdi\n2024-01-01,0.12\n", "cdi_2024-01-01_2024-01-31.csv"),
)
def test_post_exportar_csv_ok(mock_exportar, client):
    resp = client.post("/consultas-db/exportar-csv", json=_PAYLOAD_OK)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "cdi_2024" in resp.headers.get("content-disposition", "")
    assert b"data_referencia" in resp.content
    mock_exportar.assert_called_once_with(**_PAYLOAD_OK)


@pytest.mark.regression
@patch(
    "api.routers.consultas_db.exportar_csv",
    side_effect=LimiteExportacaoError(600_000, 500_000),
)
def test_post_exportar_limite(mock_exportar, client):
    resp = client.post("/consultas-db/exportar-csv", json=_PAYLOAD_OK)
    assert resp.status_code == 422
    mock_exportar.assert_called_once()


@pytest.mark.regression
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"tabela": "cdi", "colunas": []},
    ],
)
def test_post_consultar_body_invalido_pydantic(client, payload):
    resp = client.post("/consultas-db/consultar", json=payload)
    assert resp.status_code == 422
