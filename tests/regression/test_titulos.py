"""
Testes de regressão para endpoints de títulos (LTN, LFT, NTNB, NTNF).

Estes testes validam:
- Estrutura de resposta (campos obrigatórios presentes)
- Tipos de dados corretos
- Valores numéricos principais (PU, taxa, etc.)
- Campos opcionais quando presentes/ausentes
"""

import pytest


class TestLTN:
    """Testes para POST /titulos/ltn"""

    def test_criar_ltn_com_taxa(self, client, sample_vencimentos):
        """Testa criação de LTN com taxa explícita"""
        payload = {
            "data_vencimento": sample_vencimentos["ltn"],
            "taxa": 12.5,
            "quantidade": 50000,
            "dias_liquidacao": 1,
        }

        response = client.post("/titulos/ltn", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar campos obrigatórios
        assert "tipo" in data
        assert data["tipo"] == "LTN"
        assert "nome" in data
        assert "data_vencimento" in data
        assert "data_base" in data
        assert "data_liquidacao" in data
        assert "dias_liquidacao" in data
        assert "taxa" in data
        assert "quantidade" in data
        assert "financeiro" in data
        assert "pu_d0" in data

        # Validar tipos
        assert isinstance(data["tipo"], str)
        assert isinstance(data["nome"], str)
        assert isinstance(data["taxa"], (int, float))
        assert isinstance(data["quantidade"], (int, float))
        assert isinstance(data["financeiro"], (int, float))
        assert isinstance(data["pu_d0"], (int, float))

        # Validar valores numéricos principais
        assert data["taxa"] == 12.5
        assert data["quantidade"] == 50000
        assert data["pu_d0"] > 0
        assert data["financeiro"] > 0

        # Validar campos opcionais (podem estar presentes ou None)
        if "pu_termo" in data:
            assert data["pu_termo"] is None or isinstance(data["pu_termo"], (int, float))
        if "pu_carregado" in data:
            assert data["pu_carregado"] is None or isinstance(data["pu_carregado"], (int, float))
        if "dv01" in data:
            assert data["dv01"] is None or isinstance(data["dv01"], (int, float))

    def test_criar_ltn_com_financeiro(self, client, sample_vencimentos):
        """Testa criação de LTN com financeiro ao invés de quantidade"""
        payload = {
            "data_vencimento": sample_vencimentos["ltn"],
            "taxa": 12.5,
            "financeiro": 100000,
            "dias_liquidacao": 1,
        }

        response = client.post("/titulos/ltn", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar que financeiro foi usado (aceitar pequena diferença devido a arredondamento)
        assert abs(data["financeiro"] - 100000) < 1.0  # Tolerância para arredondamento
        assert data["quantidade"] > 0  # Quantidade calculada a partir do financeiro

    def test_criar_ltn_sem_taxa(self, client, sample_vencimentos):
        """Testa criação de LTN sem taxa (usa ANBIMA)"""
        payload = {
            "data_vencimento": sample_vencimentos["ltn"],
            "quantidade": 50000,
            "dias_liquidacao": 1,
        }

        response = client.post("/titulos/ltn", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar que taxa foi obtida (deve estar presente)
        assert "taxa" in data
        assert isinstance(data["taxa"], (int, float))
        assert data["taxa"] > 0


class TestLFT:
    """Testes para POST /titulos/lft"""

    def test_criar_lft_com_taxa(self, client, sample_vencimentos):
        """Testa criação de LFT com taxa explícita"""
        payload = {
            "data_vencimento": sample_vencimentos["lft"],
            "taxa": 13.0,
            "quantidade": 10000,
            "dias_liquidacao": 1,
        }

        response = client.post("/titulos/lft", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar campos obrigatórios
        assert "tipo" in data
        assert data["tipo"] == "LFT"
        assert "nome" in data
        assert "taxa" in data
        assert "pu_d0" in data
        assert "pu_termo" in data  # LFT sempre tem pu_termo

        # Validar valores numéricos principais
        assert data["taxa"] == 13.0
        assert data["quantidade"] == 10000
        assert data["pu_d0"] > 0
        assert data["pu_termo"] is not None
        assert isinstance(data["pu_termo"], (int, float))
        assert data["pu_termo"] > 0


class TestNTNB:
    """Testes para POST /titulos/ntnb"""

    def test_criar_ntnb_com_taxa(self, client, sample_vencimentos):
        """Testa criação de NTNB com taxa explícita"""
        payload = {
            "data_vencimento": sample_vencimentos["ntnb"],
            "taxa": 7.53,
            "quantidade": 10000,
            "dias_liquidacao": 1,
        }

        response = client.post("/titulos/ntnb", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar campos obrigatórios
        assert "tipo" in data
        assert data["tipo"] == "NTNB"
        assert "taxa" in data
        assert "pu_d0" in data

        # Validar valores numéricos principais
        assert data["taxa"] == 7.53
        assert data["pu_d0"] > 0


class TestNTNF:
    """Testes para POST /titulos/ntnf"""

    def test_criar_ntnf_com_taxa(self, client, sample_vencimentos):
        """Testa criação de NTNF com taxa explícita"""
        payload = {
            "data_vencimento": sample_vencimentos["ntnf"],
            "taxa": 12.5,
            "quantidade": 50000,
            "dias_liquidacao": 1,
        }

        response = client.post("/titulos/ntnf", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Validar campos obrigatórios
        assert "tipo" in data
        assert data["tipo"] == "NTNF"
        assert "taxa" in data
        assert "pu_d0" in data

        # Validar valores numéricos principais
        assert data["taxa"] == 12.5
        assert data["pu_d0"] > 0
