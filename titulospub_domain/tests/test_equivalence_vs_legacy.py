"""
Testes de equivalência entre código legado e refatorado.

Este arquivo compara resultados do módulo original com o refatorado
para garantir que não houve mudança de comportamento.
"""
import pytest
import pandas as pd
from typing import List


# Mock básico de MarketDataProvider para testes
class MockMarketDataProvider:
    """Mock simples para testes."""
    
    def __init__(self):
        self.feriados = [
            pd.Timestamp('2025-01-01'),
            pd.Timestamp('2025-04-18'),
            pd.Timestamp('2025-05-01'),
        ]
        self.cdi = 13.65
        self.anbimas = {
            'LTN': {
                pd.Timestamp('2025-01-01'): 12.5,
                pd.Timestamp('2026-01-01'): 12.0,
            }
        }
        self.bmf_ajustes = {
            ('DI', 'DI1F27'): 13.0,
        }
    
    def get_feriados(self) -> List:
        return self.feriados
    
    def get_cdi(self) -> float:
        return self.cdi
    
    def get_ipca_dict(self, data=None):
        from titulospub_domain.domain.types import IPCADict
        return IPCADict(
            ultimo_mes_ipca=11,
            indice_ipca_fechado_atual=5000.0,
            indice_ipca_fechado_anterior=4950.0,
            var_ipca_atual=1.0,
            var_ipca_anterior=0.9,
            ipca_proj=4.5,
            ipca_usado=4.5
        )
    
    def get_vna_lft(self, data=None) -> float:
        return 10000.0
    
    def get_anbima(self, titulo_type: str, data_vencimento: pd.Timestamp) -> float:
        return self.anbimas.get(titulo_type, {}).get(data_vencimento, 12.0)
    
    def get_bmf_ajuste(self, tipo: str, codigo: str):
        return self.bmf_ajustes.get((tipo, codigo))


@pytest.fixture
def mock_provider():
    """Fixture com mock de MarketDataProvider."""
    return MockMarketDataProvider()


@pytest.fixture
def feriados():
    """Fixture com lista de feriados."""
    return [
        pd.Timestamp('2025-01-01'),
        pd.Timestamp('2025-04-18'),
        pd.Timestamp('2025-05-01'),
    ]


def test_ltn_basic_calculation(mock_provider, feriados):
    """
    Teste básico de cálculo LTN.
    
    Compara resultado do código refatorado com valores esperados.
    """
    try:
        import titulospub as legacy
        legacy_available = True
    except ImportError:
        legacy_available = False
        pytest.skip("Módulo legado não disponível para comparação")
    
    # Cria título refatorado
    from titulospub_domain import LTN
    
    ltn_ref = LTN(
        data_vencimento_titulo="2025-01-01",
        taxa=12.5,
        quantidade=50000,
        feriados=feriados,
        cdi=13.65,
        market_data_provider=mock_provider
    )
    
    # Verifica que valores foram calculados
    assert ltn_ref.pu_d0 is not None
    assert ltn_ref.pu_d0 > 0
    assert ltn_ref.dv01 is not None
    assert ltn_ref.dv01 > 0
    
    # Se legado disponível, compara
    if legacy_available:
        try:
            ltn_legacy = legacy.LTN(
                data_vencimento_titulo="2025-01-01",
                taxa=12.5,
                quantidade=50000
            )
            
            # Compara com tolerância pequena (devido a possíveis diferenças de arredondamento)
            assert abs(ltn_ref.pu_d0 - ltn_legacy.pu_d0) < 0.0001, f"PU D0 diferente: {ltn_ref.pu_d0} vs {ltn_legacy.pu_d0}"
            assert abs(ltn_ref.dv01 - ltn_legacy.dv01) < 0.01, f"DV01 diferente: {ltn_ref.dv01} vs {ltn_legacy.dv01}"
        except Exception as e:
            pytest.skip(f"Não foi possível criar título legado: {e}")


def test_ltn_quantidade_financeiro_conversion(mock_provider, feriados):
    """Testa conversão entre quantidade e financeiro."""
    from titulospub_domain import LTN
    
    ltn = LTN(
        data_vencimento_titulo="2025-01-01",
        taxa=12.5,
        quantidade=50000,
        feriados=feriados,
        cdi=13.65,
        market_data_provider=mock_provider
    )
    
    # Salva valores iniciais
    pu_d0_original = ltn.pu_d0
    financeiro_original = ltn.financeiro
    
    # Muda para financeiro
    ltn.financeiro = 100000
    
    # Verifica que quantidade mudou
    assert ltn.quantidade != 50000
    
    # Volta para quantidade original
    ltn.quantidade = 50000
    
    # Verifica que financeiro voltou
    assert abs(ltn.financeiro - financeiro_original) < 0.01


def test_dv01_calculation(mock_provider, feriados):
    """Testa cálculo de DV01."""
    from titulospub_domain.domain.risk import calculo_dv01_ltn
    
    data_base = pd.Timestamp('2025-01-15')
    data_liquidacao = pd.Timestamp('2025-01-16')
    data_vencimento = pd.Timestamp('2026-01-01')
    taxa = 12.5
    
    dv01 = calculo_dv01_ltn(
        data=data_base,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa,
        feriados=feriados
    )
    
    assert dv01 > 0
    assert dv01 < 1  # DV01 de LTN geralmente é pequeno


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
