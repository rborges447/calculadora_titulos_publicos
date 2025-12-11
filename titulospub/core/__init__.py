#!/usr/bin/env python3
"""
Módulo core - Classes principais dos títulos públicos

Este módulo contém todas as classes de títulos públicos disponíveis:
- NTNB: Títulos Públicos Indexados ao IPCA
- LTN: Letras do Tesouro Nacional
- LFT: Letras Financeiras do Tesouro  
- NTNF: Notas do Tesouro Nacional - Série F

Exemplo de uso:
    from titulospub.core import NTNB, LTN, LFT, NTNF
    
    # Criar títulos
    ntnb = NTNB("2035-05-15", taxa=7.53)
    ltn = LTN("2025-01-01", taxa=12.5)
    lft = LFT("2025-01-01", taxa=12.5)
    ntnf = NTNF("2025-01-01", taxa=12.5)
"""

# Importar todas as classes de títulos
from .ntnb.titulo_ntnb import NTNB
from .ltn.titulo_ltn import LTN
from .lft.titulo_lft import LFT
from .ntnf.titulo_ntnf import NTNF
from .di.di_contrato import DI

# Importar funções de cálculo de DI
from .di.calculo_di import taxa_pu_di, calculo_dv01_di

# Importar funções de cálculo de DAP
from .dap.calculo_dap import dia_15_do_mes, calculo_prt, calculo_pu_dap, calculo_financeiro_dap

# Importar função de equivalência
from .equivalencia import equivalencia

# Lista de todas as classes disponíveis
__all__ = [
    'NTNB',
    'LTN', 
    'LFT',
    'NTNF',
    'DI',
    'equivalencia',
    'taxa_pu_di',
    'calculo_dv01_di',
    'dia_15_do_mes',
    'calculo_prt',
    'calculo_pu_dap',
    'calculo_financeiro_dap'
]

# Versão do módulo
__version__ = "1.0.0"

# Informações sobre o módulo
__author__ = "Sistema de Cálculo de Títulos Públicos"
__description__ = "Classes para cálculo e análise de títulos públicos brasileiros"

# Documentação das classes
NTNB.__doc__ = """
NTNB - Títulos Públicos Indexados ao IPCA

Classe para cálculo de títulos públicos indexados ao IPCA (NTN-B).
Permite definir posições por quantidade ou valor financeiro.

Atributos principais:
- quantidade: Número de títulos
- financeiro: Valor financeiro da posição (R$)
- pu_d0: Preço unitário
- dv01: Sensibilidade à mudança de 1bp na taxa
- carrego_brl: Carregamento em reais

Exemplo:
    ntnb = NTNB("2035-05-15", taxa=7.53)
    ntnb.financeiro = 100000  # Define posição por valor
    print(f"Quantidade: {ntnb.quantidade:,.0f}")
"""

LTN.__doc__ = """
LTN - Letras do Tesouro Nacional

Classe para cálculo de Letras do Tesouro Nacional (LTN).
Títulos prefixados com vencimento em data específica.

Atributos principais:
- quantidade: Número de títulos
- financeiro: Valor financeiro da posição (R$)
- pu_d0: Preço unitário
- dv01: Sensibilidade à mudança de 1bp na taxa
- carrego_brl: Carregamento em reais

Exemplo:
    ltn = LTN("2025-01-01", taxa=12.5)
    ltn.quantidade = 50000  # Define posição por quantidade
    print(f"Financeiro: R$ {ltn.financeiro:,.2f}")
"""

LFT.__doc__ = """
LFT - Letras Financeiras do Tesouro

Classe para cálculo de Letras Financeiras do Tesouro (LFT).
Títulos pós-fixados indexados à taxa Selic.

Atributos principais:
- quantidade: Número de títulos
- financeiro: Valor financeiro da posição (R$)
- pu_d0: Preço unitário
- pu_termo: Preço a termo
- pu_carregado: Preço carregado

Exemplo:
    lft = LFT("2025-01-01", taxa=12.5)
    lft.financeiro = 75000  # Define posição por valor
    print(f"Quantidade: {lft.quantidade:,.0f}")
"""

NTNF.__doc__ = """
NTNF - Notas do Tesouro Nacional - Série F

Classe para cálculo de Notas do Tesouro Nacional - Série F (NTN-F).
Títulos prefixados com cupom semestral.

Atributos principais:
- quantidade: Número de títulos
- financeiro: Valor financeiro da posição (R$)
- pu_d0: Preço unitário
- dv01: Sensibilidade à mudança de 1bp na taxa
- carrego_brl: Carregamento em reais

Exemplo:
    ntnf = NTNF("2025-01-01", taxa=12.5)
    ntnf.quantidade = 30000  # Define posição por quantidade
    print(f"Financeiro: R$ {ntnf.financeiro:,.2f}")
"""

DI.__doc__ = """
DI - Contratos de Depósito Interbancário

Classe para cálculo de contratos de Depósito Interbancário (DI).
Títulos pós-fixados indexados à taxa CDI.

Atributos principais:
- quantidade: Número de contratos
- financeiro: Valor financeiro da posição (R$)
- pu: Preço unitário
- dv01: Sensibilidade à mudança de 1bp na taxa

Exemplo:
    di = DI(codigo="DI1F27", taxa=13.5)
    di.quantidade = 1000  # Define posição por quantidade
    print(f"Financeiro: R$ {di.financeiro:,.2f}")
"""

def get_titulos_disponiveis():
    """
    Retorna uma lista com todos os tipos de títulos disponíveis
    
    Returns:
        list: Lista com os nomes das classes de títulos
    """
    return __all__.copy()

def criar_titulo(tipo_titulo, data_vencimento, **kwargs):
    """
    Função factory para criar títulos de forma dinâmica
    
    Args:
        tipo_titulo (str): Tipo do título ('NTNB', 'LTN', 'LFT', 'NTNF')
        data_vencimento (str): Data de vencimento do título
        **kwargs: Parâmetros adicionais para o construtor do título
    
    Returns:
        Título: Instância do título criado
        
    Raises:
        ValueError: Se o tipo de título não for reconhecido
    """
    titulos_disponiveis = {
        'NTNB': NTNB,
        'LTN': LTN,
        'LFT': LFT,
        'NTNF': NTNF,
        'DI': DI
    }
    
    if tipo_titulo not in titulos_disponiveis:
        raise ValueError(f"Tipo de título '{tipo_titulo}' não reconhecido. "
                        f"Tipos disponíveis: {list(titulos_disponiveis.keys())}")
    
    return titulos_disponiveis[tipo_titulo](data_vencimento, **kwargs)

def listar_titulos():
    """
    Exibe informações sobre todos os tipos de títulos disponíveis
    """
    print("📋 TÍTULOS PÚBLICOS DISPONÍVEIS")
    print("=" * 50)
    
    titulos_info = {
        'NTNB': {
            'nome': 'Títulos Públicos Indexados ao IPCA',
            'caracteristica': 'Indexado ao IPCA',
            'cupom': 'Semestral'
        },
        'LTN': {
            'nome': 'Letras do Tesouro Nacional',
            'caracteristica': 'Prefixado',
            'cupom': 'Zero cupom'
        },
        'LFT': {
            'nome': 'Letras Financeiras do Tesouro',
            'caracteristica': 'Pós-fixado (Selic)',
            'cupom': 'Zero cupom'
        },
        'NTNF': {
            'nome': 'Notas do Tesouro Nacional - Série F',
            'caracteristica': 'Prefixado',
            'cupom': 'Semestral'
        },
        'DI': {
            'nome': 'Contratos de Depósito Interbancário',
            'caracteristica': 'Pós-fixado (CDI)',
            'cupom': 'Zero cupom'
        }
    }
    
    for sigla, info in titulos_info.items():
        print(f"📊 {sigla}: {info['nome']}")
        print(f"   Característica: {info['caracteristica']}")
        print(f"   Cupom: {info['cupom']}")
        print()
    
    print("💡 Exemplo de uso:")
    print("   from titulospub.core import NTNB, LTN, LFT, NTNF")
    print("   ntnb = NTNB('2035-05-15', taxa=7.53)")
    print("   ntnb.financeiro = 100000")
