"""
Módulo de dados para o projeto de calculadora de títulos públicos.

Normalizers (ANBIMA, BMF, IPCA, backups) em ``transforms/``.
"""

from .cache import (
    clear_cache,
    load_cache,
    save_cache,
)
from .orquestrador import (
    VariaveisMercado,
)
from .transforms import (
    anbimas,
    ajustes_bmf,
    ajustes_bmf_net,
    backup_anbimas,
    backup_bmf,
    backup_cdi,
    backup_feriados,
    backup_ipca_fechado,
    backup_ipca_proj,
    inicio_fim_mes_ipca,
    ipca_dict_from_db,
    transform_ipca,
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
    'inicio_fim_mes_ipca',
    'ipca_dict_from_db',
    'transform_ipca',
    
    # Classe principal
    'VariaveisMercado'
]

# Versão do módulo
__version__ = "1.0.0"
