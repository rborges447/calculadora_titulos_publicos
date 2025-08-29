"""
Módulo de scraping para coleta de dados de mercado.

Este módulo contém funções para fazer scraping de dados de diferentes fontes:
- ANBIMA: Dados de títulos públicos
- SIDRA: Dados do IPCA
- UpToData: Dados da BMF
"""

# Imports principais do módulo anbima_scraping
from .anbima_scraping import (
    scrap_cdi,
    scrap_feriados,
    scrap_proj_ipca,
    scrap_anbimas
)

# Imports principais do módulo sidra_scraping
from .sidra_scraping import (
    puxar_valores_ipca_fechado
)

# Imports principais do módulo uptodata_scraping
from .uptodata_scraping import (
    scrap_ajustes_bmf
)

__all__ = [
    # ANBIMA scraping
    'scrap_cdi',
    'scrap_feriados', 
    'scrap_proj_ipca',
    'scrap_anbimas',
    
    # SIDRA scraping
    'puxar_valores_ipca_fechado',
    
    # UpToData scraping
    'scrap_ajustes_bmf'
]

# Versão do módulo
__version__ = "1.0.0"
