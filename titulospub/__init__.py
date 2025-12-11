#!/usr/bin/env python3
"""
Módulo titulospub - Sistema de Cálculo de Títulos Públicos Brasileiros

Este módulo contém todas as funcionalidades para cálculo e análise de títulos públicos:
- Classes de títulos: NTNB, LTN, LFT, NTNF, DI
- Funções de scraping de dados de mercado
- Utilitários para manipulação de datas e arquivos
- Sistema de cache e backup de dados

Exemplo de uso:
    from titulospub import NTNB, LTN, LFT, NTNF, DI
    
    # Criar títulos
    ntnb = NTNB("2035-05-15", taxa=7.53)
    ltn = LTN("2025-01-01", taxa=12.5)
    di = DI(codigo="DI1F27", taxa=13.5)
    
    # Definir posições
    ntnb.financeiro = 100000
    ltn.quantidade = 50000
    di.quantidade = 1000
"""

# Importar classes de títulos do módulo core
from .core import NTNB, LTN, LFT, NTNF, DI

# Importar função de equivalência
from .core.equivalencia import equivalencia

# Importar funções principais de cada módulo
from .scraping import (
    scrap_cdi,
    scrap_feriados,
    scrap_proj_ipca,
    scrap_anbimas,
    scrap_vna_lft,
    puxar_valores_ipca_fechado,
    definir_caminho_adj_bmf,
    scrap_ajustes_bmf,
    scrap_bmf_net
)

from .utils import (
    adicionar_dias_uteis,
    e_dia_util,
    dias_trabalho_total,
    listar_dias_entre_datas,
    ajustar_para_proximo_dia_util,
    listar_datas,
    data_vencimento_ajustada,
    datas_pagamento_cupons,
    path_backup_csv,
    path_backup_pickle,
    path_logs,
    _carrecar_cdi_se_necessario,
    _carrecar_ipca_dict_se_necessario,
    _carregar_feriados_se_necessario,
    _carregar_vna_lft_se_necessario
)

from .dados import (
    backup_cdi,
    backup_feriados,
    backup_ipca_fechado,
    backup_ipca_proj,
    backup_anbimas,
    backup_bmf,
    save_cache,
    load_cache,
    clear_cache,
    anbimas,
    ajustes_bmf,
    ajustes_bmf_net,
    dicionario_ipca,
    VariaveisMercado
)

# Lista de todas as classes e funções disponíveis
__all__ = [
    # Classes de títulos
    'NTNB',
    'LTN',
    'LFT',
    'NTNF',
    'DI',
    
    # Função de equivalência
    'equivalencia',
    
    # Funções de scraping
    'scrap_cdi',
    'scrap_feriados',
    'scrap_proj_ipca',
    'scrap_anbimas',
    'scrap_vna_lft',
    'puxar_valores_ipca_fechado',
    'definir_caminho_adj_bmf',
    'scrap_ajustes_bmf',
    'scrap_bmf_net',
    
    # Funções utilitárias
    'adicionar_dias_uteis',
    'e_dia_util',
    'dias_trabalho_total',
    'listar_dias_entre_datas',
    'ajustar_para_proximo_dia_util',
    'listar_datas',
    'data_vencimento_ajustada',
    'datas_pagamento_cupons',
    'path_backup_csv',
    'path_backup_pickle',
    'path_logs',
    '_carrecar_cdi_se_necessario',
    '_carrecar_ipca_dict_se_necessario',
    '_carregar_feriados_se_necessario',
    '_carregar_vna_lft_se_necessario',
    
    # Funções de dados
    'backup_cdi',
    'backup_feriados',
    'backup_ipca_fechado',
    'backup_ipca_proj',
    'backup_anbimas',
    'backup_bmf',
    'save_cache',
    'load_cache',
    'clear_cache',
    'anbimas',
    'ajustes_bmf',
    'ajustes_bmf_net',
    'dicionario_ipca',
    'VariaveisMercado'
]

# Versão do módulo
__version__ = "1.0.0"

# Informações sobre o módulo
__author__ = "Sistema de Cálculo de Títulos Públicos"
__description__ = "Sistema completo para cálculo e análise de títulos públicos brasileiros"

def get_info_modulos():
    """
    Retorna informações sobre todos os submódulos disponíveis
    
    Returns:
        dict: Dicionário com informações dos módulos
    """
    return {
        'core': {
            'descricao': 'Classes principais dos títulos públicos',
            'classes': ['NTNB', 'LTN', 'LFT', 'NTNF', 'DI'],
            'versao': '1.0.0'
        },
        'scraping': {
            'descricao': 'Funções para coleta de dados de mercado',
            'funcoes': ['scrap_cdi', 'scrap_feriados', 'scrap_anbimas', 'scrap_vna_lft', 'scrap_bmf_net'],
            'versao': '1.0.0'
        },
        'utils': {
            'descricao': 'Utilitários para manipulação de datas e arquivos',
            'funcoes': ['adicionar_dias_uteis', 'e_dia_util', 'path_backup_csv'],
            'versao': '1.0.0'
        },
        'dados': {
            'descricao': 'Sistema de cache, backup e processamento de dados',
            'funcoes': ['VariaveisMercado', 'save_cache', 'backup_cdi'],
            'versao': '1.0.0'
        }
    }

def listar_funcionalidades():
    """
    Exibe todas as funcionalidades disponíveis no módulo
    """
    print("📋 FUNCIONALIDADES DO MÓDULO TITULOSPUB")
    print("=" * 60)
    
    print("\n🎯 CLASSES DE TÍTULOS:")
    print("   - NTNB: Títulos Públicos Indexados ao IPCA")
    print("   - LTN: Letras do Tesouro Nacional")
    print("   - LFT: Letras Financeiras do Tesouro")
    print("   - NTNF: Notas do Tesouro Nacional - Série F")
    print("   - DI: Contratos de Depósito Interbancário")
    
    print("\n🔍 FUNÇÕES DE SCRAPING:")
    print("   - scrap_cdi: Coleta dados do CDI")
    print("   - scrap_feriados: Coleta feriados")
    print("   - scrap_anbimas: Coleta dados ANBIMA")
    print("   - scrap_vna_lft: Coleta VNA LFT")
    print("   - scrap_bmf_net: Coleta dados BMF")
    
    print("\n⚙️ FUNÇÕES UTILITÁRIAS:")
    print("   - adicionar_dias_uteis: Adiciona dias úteis")
    print("   - e_dia_util: Verifica se é dia útil")
    print("   - path_backup_csv: Caminho para backup CSV")
    
    print("\n💾 FUNÇÕES DE DADOS:")
    print("   - VariaveisMercado: Orquestrador de dados")
    print("   - save_cache: Salva cache")
    print("   - backup_cdi: Backup do CDI")
    
    print("\n💡 EXEMPLO DE USO:")
    print("   from titulospub import NTNB, LTN, equivalencia")
    print("   ntnb = NTNB('2035-05-15', taxa=7.53)")
    print("   ntnb.financeiro = 100000")
    print("   eq = equivalencia('NTNB', '2035-05-15', 'LTN', '2025-01-01', qtd1=10000, criterio='dv')")

def criar_titulo(tipo_titulo, data_vencimento, **kwargs):
    """
    Função factory para criar títulos de forma dinâmica
    
    Args:
        tipo_titulo (str): Tipo do título ('NTNB', 'LTN', 'LFT', 'NTNF', 'DI')
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
