"""
Módulo de dados para o projeto de calculadora de títulos públicos.

Este módulo contém:
- Funções de backup para dados de mercado
- Sistema de cache para otimização
- Processamento de dados ANBIMA, BMF e IPCA
- Orquestrador de variáveis de mercado
"""

# Imports principais do módulo backup
from .backup import (
    backup_cdi,
    backup_feriados,
    backup_ipca_fechado,
    backup_ipca_proj,
    backup_anbimas,
    backup_bmf
)

# Imports principais do módulo cache
from .cache import (
    save_cache,
    load_cache,
    clear_cache
)

# Imports principais do módulo anbimas
from .anbimas import (
    anbimas
)

# Imports principais do módulo bmf
from .bmf import (
    ajustes_bmf,
    ajustes_bmf_net
)

# Imports principais do módulo ipca
from .ipca import (
    dicionario_ipca
)

# Imports principais do módulo orquestrador
from .orquestrador import (
    VariaveisMercado
)

__all__ = [
    # Funções de backup
    'backup_cdi',
    'backup_feriados',
    'backup_ipca_fechado',
    'backup_ipca_proj',
    'backup_anbimas',
    'backup_bmf',
    
    # Funções de cache
    'save_cache',
    'load_cache',
    'clear_cache',
    
    # Funções de processamento
    'anbimas',
    'ajustes_bmf',
    'ajustes_bmf_net',
    'dicionario_ipca',
    
    # Classe principal
    'VariaveisMercado'
]

# Versão do módulo
__version__ = "1.0.0" 