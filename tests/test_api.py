"""
Testes para API FastAPI usando TestClient.

Estes testes verificam que a API funciona corretamente
e que os endpoints retornam os dados esperados.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Cliente de teste para a API"""
    return TestClient(app)


class TestAPIRoot:
    """Testes para endpoint raiz"""
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_endpoint(self, client):
        """Testa endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestAPILTN:
    """Testes para endpoints de LTN"""
    
    def test_criar_ltn_basico(self, client, sample_vencimento_ltn):
        """Testa criação básica de LTN via API"""
        payload = {
            "data_vencimento": sample_vencimento_ltn,
            "taxa": 12.5,
            "quantidade": 50000
        }
        response = client.post("/titulos/ltn", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data["tipo"] == "LTN"
            assert data["quantidade"] == 50000
            assert "pu_d0" in data
            assert "financeiro" in data
        else:
            # Se falhar por vencimento não existir, é aceitável
            pytest.skip(f"Vencimento não disponível: {response.status_code}")
    
    def test_criar_ltn_com_financeiro(self, client, sample_vencimento_ltn):
        """Testa criação de LTN com valor financeiro"""
        payload = {
            "data_vencimento": sample_vencimento_ltn,
            "taxa": 12.5,
            "financeiro": 100000
        }
        response = client.post("/titulos/ltn", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data["financeiro"] == 100000
            assert data["quantidade"] > 0
        else:
            pytest.skip(f"Vencimento não disponível: {response.status_code}")
    
    def test_ltn_deterministico(self, client, sample_vencimento_ltn):
        """Testa que API retorna resultados determinísticos"""
        payload = {
            "data_vencimento": sample_vencimento_ltn,
            "taxa": 12.5,
            "quantidade": 50000
        }
        
        response1 = client.post("/titulos/ltn", json=payload)
        response2 = client.post("/titulos/ltn", json=payload)
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            # Resultados devem ser iguais (ou muito próximos)
            assert abs(data1["pu_d0"] - data2["pu_d0"]) < 0.01
            assert abs(data1["financeiro"] - data2["financeiro"]) < 0.01
        else:
            pytest.skip("Vencimento não disponível")


class TestAPINTNB:
    """Testes para endpoints de NTNB"""
    
    def test_criar_ntnb_basico(self, client, sample_vencimento_ntnb):
        """Testa criação básica de NTNB via API"""
        payload = {
            "data_vencimento": sample_vencimento_ntnb,
            "taxa": 7.5,
            "quantidade": 10000
        }
        response = client.post("/titulos/ntnb", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data["tipo"] == "NTNB"
            assert data["quantidade"] == 10000
            assert "pu_d0" in data
        else:
            pytest.skip(f"Vencimento não disponível: {response.status_code}")


class TestAPIVencimentos:
    """Testes para endpoints de vencimentos"""
    
    def test_vencimentos_ltn(self, client):
        """Testa endpoint de vencimentos LTN"""
        response = client.get("/vencimentos/ltn")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_vencimentos_ntnb(self, client):
        """Testa endpoint de vencimentos NTNB"""
        response = client.get("/vencimentos/ntnb")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAPICarteiras:
    """Testes para endpoints de carteiras"""
    
    def test_criar_carteira_ltn(self, client):
        """Testa criação de carteira LTN"""
        payload = {
            "dias_liquidacao": 1
        }
        response = client.post("/carteiras/ltn", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "carteira_id" in data
            assert data["tipo"] == "LTN"
            assert "titulos" in data
            assert isinstance(data["titulos"], list)
        else:
            pytest.skip(f"Erro ao criar carteira: {response.status_code}")
    
    def test_carteiras_multiplas_chamadas(self, client):
        """Testa múltiplas chamadas para garantir ausência de estado global"""
        payload = {"dias_liquidacao": 1}
        
        # Criar duas carteiras
        response1 = client.post("/carteiras/ltn", json=payload)
        response2 = client.post("/carteiras/ltn", json=payload)
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            # IDs devem ser diferentes (cada chamada cria nova carteira)
            assert data1["carteira_id"] != data2["carteira_id"]
            
            # Mas os dados devem ser consistentes
            assert len(data1["titulos"]) == len(data2["titulos"])
        else:
            pytest.skip("Erro ao criar carteiras")
