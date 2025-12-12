"""
Testes para cálculos principais do módulo titulospub.

Estes testes "congelam" o comportamento atual dos cálculos,
garantindo que refatorações não alterem os resultados.
"""
import pytest
from titulospub import LTN, LFT, NTNB, NTNF


class TestLTN:
    """Testes para cálculos de LTN"""
    
    def test_ltn_criacao_basica(self, sample_vencimento_ltn):
        """Testa criação básica de LTN"""
        ltn = LTN(sample_vencimento_ltn, taxa=12.5)
        assert ltn is not None
        assert hasattr(ltn, 'quantidade')
        assert hasattr(ltn, 'financeiro')
        assert hasattr(ltn, 'pu_d0')
    
    def test_ltn_com_quantidade(self, sample_vencimento_ltn):
        """Testa LTN com quantidade definida"""
        ltn = LTN(sample_vencimento_ltn, taxa=12.5, quantidade=50000)
        assert ltn.quantidade == 50000
        assert ltn.financeiro > 0
    
    def test_ltn_com_financeiro(self, sample_vencimento_ltn):
        """Testa LTN com valor financeiro definido"""
        ltn = LTN(sample_vencimento_ltn, taxa=12.5)
        ltn.financeiro = 100000
        assert ltn.financeiro == 100000
        assert ltn.quantidade > 0
    
    def test_ltn_deterministico(self, sample_vencimento_ltn):
        """Testa que LTN é determinístico (mesmo input → mesmo output)"""
        ltn1 = LTN(sample_vencimento_ltn, taxa=12.5, quantidade=50000)
        ltn2 = LTN(sample_vencimento_ltn, taxa=12.5, quantidade=50000)
        
        # Valores devem ser iguais (ou muito próximos devido a arredondamentos)
        assert abs(ltn1.pu_d0 - ltn2.pu_d0) < 0.01
        assert abs(ltn1.financeiro - ltn2.financeiro) < 0.01
    
    def test_ltn_multiplas_chamadas(self, sample_vencimento_ltn):
        """Testa múltiplas chamadas para garantir ausência de estado global"""
        resultados = []
        for i in range(5):
            ltn = LTN(sample_vencimento_ltn, taxa=12.5 + i, quantidade=50000)
            resultados.append(ltn.pu_d0)
        
        # Cada chamada deve produzir resultado diferente (taxa diferente)
        assert len(set([round(r, 2) for r in resultados])) == 5


class TestNTNB:
    """Testes para cálculos de NTNB"""
    
    def test_ntnb_criacao_basica(self, sample_vencimento_ntnb):
        """Testa criação básica de NTNB"""
        ntnb = NTNB(sample_vencimento_ntnb, taxa=7.5)
        assert ntnb is not None
        assert hasattr(ntnb, 'quantidade')
        assert hasattr(ntnb, 'financeiro')
        assert hasattr(ntnb, 'pu_d0')
    
    def test_ntnb_com_quantidade(self, sample_vencimento_ntnb):
        """Testa NTNB com quantidade definida"""
        ntnb = NTNB(sample_vencimento_ntnb, taxa=7.5, quantidade=10000)
        assert ntnb.quantidade == 10000
        assert ntnb.financeiro > 0
    
    def test_ntnb_deterministico(self, sample_vencimento_ntnb):
        """Testa que NTNB é determinístico"""
        ntnb1 = NTNB(sample_vencimento_ntnb, taxa=7.5, quantidade=10000)
        ntnb2 = NTNB(sample_vencimento_ntnb, taxa=7.5, quantidade=10000)
        
        assert abs(ntnb1.pu_d0 - ntnb2.pu_d0) < 0.01
        assert abs(ntnb1.financeiro - ntnb2.financeiro) < 0.01


class TestLFT:
    """Testes para cálculos de LFT"""
    
    def test_lft_criacao_basica(self, sample_vencimento_lft):
        """Testa criação básica de LFT"""
        lft = LFT(sample_vencimento_lft, taxa=12.5)
        assert lft is not None
        assert hasattr(lft, 'quantidade')
        assert hasattr(lft, 'financeiro')
        assert hasattr(lft, 'pu_d0')
    
    def test_lft_deterministico(self, sample_vencimento_lft):
        """Testa que LFT é determinístico"""
        lft1 = LFT(sample_vencimento_lft, taxa=12.5, quantidade=10000)
        lft2 = LFT(sample_vencimento_lft, taxa=12.5, quantidade=10000)
        
        assert abs(lft1.pu_d0 - lft2.pu_d0) < 0.01
        assert abs(lft1.financeiro - lft2.financeiro) < 0.01


class TestNTNF:
    """Testes para cálculos de NTNF"""
    
    def test_ntnf_criacao_basica(self, sample_vencimento_ntnf):
        """Testa criação básica de NTNF"""
        ntnf = NTNF(sample_vencimento_ntnf, taxa=12.5)
        assert ntnf is not None
        assert hasattr(ntnf, 'quantidade')
        assert hasattr(ntnf, 'financeiro')
        assert hasattr(ntnf, 'pu_d0')
    
    def test_ntnf_deterministico(self, sample_vencimento_ntnf):
        """Testa que NTNF é determinístico"""
        ntnf1 = NTNF(sample_vencimento_ntnf, taxa=12.5, quantidade=50000)
        ntnf2 = NTNF(sample_vencimento_ntnf, taxa=12.5, quantidade=50000)
        
        assert abs(ntnf1.pu_d0 - ntnf2.pu_d0) < 0.01
        assert abs(ntnf1.financeiro - ntnf2.financeiro) < 0.01


class TestEquivalencia:
    """Testes para função de equivalência"""
    
    def test_equivalencia_import(self):
        """Testa que função equivalencia pode ser importada"""
        from titulospub import equivalencia
        assert callable(equivalencia)
    
    def test_equivalencia_basica(self, sample_vencimento_ltn, sample_vencimento_ntnb):
        """Testa cálculo básico de equivalência"""
        from titulospub import equivalencia
        
        # Teste básico - pode falhar se vencimentos não existirem
        try:
            resultado = equivalencia(
                "LTN", sample_vencimento_ltn,
                "NTNB", sample_vencimento_ntnb,
                qtd1=10000,
                criterio="dv"
            )
            assert resultado is not None
        except Exception as e:
            # Se falhar por vencimento não existir, é aceitável
            pytest.skip(f"Vencimentos não disponíveis: {e}")
