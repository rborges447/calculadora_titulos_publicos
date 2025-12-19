"""
Testes de regressão para GET /vencimentos/*.
"""

import pytest


class TestVencimentos:
    """Testes para endpoints de vencimentos"""

    def test_get_vencimentos_ltn(self, client):
        """Testa GET /vencimentos/ltn (retorna lista diretamente)"""
        response = client.get("/vencimentos/ltn")
        assert response.status_code == 200

        data = response.json()

        # Validar que é uma lista
        assert isinstance(data, list)

        # Validar formato de datas (se houver vencimentos)
        if data:
            for venc in data:
                assert isinstance(venc, str)
                # Formato YYYY-MM-DD
                assert len(venc) == 10
                assert venc[4] == "-"
                assert venc[7] == "-"

    def test_get_vencimentos_ltn_detalhes(self, client):
        """Testa GET /vencimentos/ltn/detalhes (retorna estrutura com metadados)"""
        response = client.get("/vencimentos/ltn/detalhes")
        assert response.status_code == 200

        data = response.json()

        # Validar estrutura
        assert "vencimentos" in data
        assert "total" in data

        # Validar tipos
        assert isinstance(data["vencimentos"], list)
        assert isinstance(data["total"], int)

        # Validar que total corresponde ao tamanho da lista
        assert data["total"] == len(data["vencimentos"])

    def test_get_vencimentos_lft(self, client):
        """Testa GET /vencimentos/lft (retorna lista diretamente)"""
        response = client.get("/vencimentos/lft")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_vencimentos_ntnb(self, client):
        """Testa GET /vencimentos/ntnb (retorna lista diretamente)"""
        response = client.get("/vencimentos/ntnb")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_vencimentos_ntnf(self, client):
        """Testa GET /vencimentos/ntnf (retorna lista diretamente)"""
        response = client.get("/vencimentos/ntnf")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_todos_vencimentos(self, client):
        """Testa GET /vencimentos/todos"""
        response = client.get("/vencimentos/todos")
        assert response.status_code == 200

        data = response.json()

        # Validar estrutura
        assert "ltn" in data
        assert "lft" in data
        assert "ntnb" in data
        assert "ntnf" in data

        # Validar tipos
        assert isinstance(data["ltn"], list)
        assert isinstance(data["lft"], list)
        assert isinstance(data["ntnb"], list)
        assert isinstance(data["ntnf"], list)
