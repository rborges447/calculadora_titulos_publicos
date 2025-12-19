"""
Testes de regressão para POST /equivalencia.
"""

import pytest


class TestEquivalencia:
    """Testes para cálculo de equivalência entre títulos"""

    def test_equivalencia_dv01_ltn_ntnb(self, client, sample_vencimentos):
        """Testa equivalência por DV01 entre LTN e NTNB"""
        payload = {
            "titulo1": "LTN",
            "venc1": sample_vencimentos["ltn"],
            "titulo2": "NTNB",
            "venc2": sample_vencimentos["ntnb"],
            "qtd1": 10000,
            "criterio": "dv",
        }

        response = client.post("/equivalencia", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar estrutura de resposta
        assert "titulo1" in data
        assert "titulo2" in data
        assert "venc1" in data
        assert "venc2" in data
        assert "qtd1" in data
        assert "equivalencia" in data
        assert "criterio" in data

        # Validar valores
        assert data["titulo1"] == "LTN"
        assert data["titulo2"] == "NTNB"
        assert data["qtd1"] == 10000
        assert data["criterio"] == "dv"
        assert isinstance(data["equivalencia"], (int, float))
        assert data["equivalencia"] > 0

    def test_equivalencia_financeiro_ltn_ntnb(self, client, sample_vencimentos):
        """Testa equivalência financeira entre LTN e NTNB"""
        payload = {
            "titulo1": "LTN",
            "venc1": sample_vencimentos["ltn"],
            "titulo2": "NTNB",
            "venc2": sample_vencimentos["ntnb"],
            "qtd1": 10000,
            "criterio": "fin",
        }

        response = client.post("/equivalencia", json=payload)
        assert response.status_code == 200

        data = response.json()

        assert data["criterio"] == "fin"
        assert isinstance(data["equivalencia"], (int, float))
        assert data["equivalencia"] > 0

    def test_equivalencia_lft_apenas_financeiro(self, client, sample_vencimentos):
        """Testa que LFT não suporta equivalência por DV01"""
        payload = {
            "titulo1": "LFT",
            "venc1": sample_vencimentos["lft"],
            "titulo2": "LTN",
            "venc2": sample_vencimentos["ltn"],
            "qtd1": 10000,
            "criterio": "dv",  # LFT não suporta DV01
        }

        response = client.post("/equivalencia", json=payload)
        # Deve retornar erro 422 ou 400
        assert response.status_code in [400, 422]
