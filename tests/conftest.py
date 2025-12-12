"""
Configuração global do pytest para testes do projeto.
"""
import pytest
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def api_base_url():
    """URL base da API para testes"""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def sample_vencimento_ltn():
    """Vencimento de exemplo para LTN (deve existir no sistema)"""
    # Usar um vencimento que provavelmente existe
    return "2026-01-01"


@pytest.fixture(scope="session")
def sample_vencimento_ntnb():
    """Vencimento de exemplo para NTNB (deve existir no sistema)"""
    return "2035-05-15"


@pytest.fixture(scope="session")
def sample_vencimento_lft():
    """Vencimento de exemplo para LFT (deve existir no sistema)"""
    return "2026-01-01"


@pytest.fixture(scope="session")
def sample_vencimento_ntnf():
    """Vencimento de exemplo para NTNF (deve existir no sistema)"""
    return "2026-01-01"
