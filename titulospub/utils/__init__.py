"""
Módulo de utilitários para o projeto.

Este módulo contém funções utilitárias para:
- Manipulação de datas
- Gerenciamento de caminhos de arquivos
"""

# Imports principais do módulo datas
from .datas import (
    adicionar_dias_uteis,
    e_dia_util,
    dias_trabalho_total,
    listar_dias_entre_datas,
    ajustar_para_proximo_dia_util,
    listar_datas,
    data_vencimento_ajustada,
    datas_pagamento_cupons
)

# Imports principais do módulo paths
from .paths import (
    path_backup_csv,
    path_backup_pickle,
    path_logs
)

# Imports principais do módodulo de carregamento
from.carregamento_var_globais import (_carrecar_cdi_se_necessario,
            _carrecar_ipca_dict_se_necessario,
            _carregar_feriados_se_necessario,
            _carregar_vna_lft_se_necessario)

__all__ = [
    # Funções de datas
    'adicionar_dias_uteis',
    'e_dia_util',
    'dias_trabalho_total',
    'listar_dias_entre_datas',
    'ajustar_para_proximo_dia_util',
    'listar_datas',
    'data_vencimento_ajustada',
    "datas_pagamento_cupons",
    
    # Funções de paths
    'path_backup_csv',
    'path_backup_pickle',
    'path_logs',

    # Funções de carregamento
    '_carrecar_cdi_se_necessario',
    '_carrecar_ipca_dict_se_necessario',
    '_carregar_feriados_se_necessario',
    '_carregar_vna_lft_se_necessario'
]

# Versão do módulo
__version__ = "1.0.0" 