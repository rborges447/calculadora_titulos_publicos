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
    scrap_anbimas,
    scrap_vna_lft
)

# Imports principais do módulo sidra_scraping
from .sidra_scraping import (
    puxar_valores_ipca_fechado
)

# Imports principais do módulo uptodata_scraping
from .uptodata_scraping import (
    definir_caminho_adj_bmf,
    scrap_ajustes_bmf
)

# Imports principais do módulo bmf_net_scraping
from .bmf_net_scraping import (
    scrap_bmf_net
)

__all__ = [
    # ANBIMA scraping
    'scrap_cdi',
    'scrap_feriados', 
    'scrap_proj_ipca',
    'scrap_anbimas',
    'scrap_vna_lft',
    
    # SIDRA scraping
    'puxar_valores_ipca_fechado',
    
    # UpToData scraping
    'definir_caminho_adj_bmf',
    'scrap_ajustes_bmf',

    #bmf_net_scaping
    'scrap_bmf_net'
]

# Versão do módulo
__version__ = "1.0.0"
