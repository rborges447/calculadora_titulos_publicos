"""
Fixtures compartilhadas para testes de regressão.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """
    Cliente de teste FastAPI.

    NOTA: O lifespan da aplicação será executado, mas tentará usar cache/backup
    se disponível para evitar scraping durante testes.
    """
    return TestClient(app)


@pytest.fixture
def sample_vencimentos():
    """
    Vencimentos de exemplo para testes.
    Estes são vencimentos válidos que existem nos dados de mercado.
    """
    return {
        "ltn": "2026-01-01",  # Vencimento real disponível
        "lft": "2026-03-01",  # Vencimento real disponível
        "ntnb": "2026-08-15",  # Vencimento real disponível
        "ntnf": "2027-01-01",  # Vencimento real disponível
    }
