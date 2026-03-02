"""
titulospub_domain - Módulo de domínio refatorado para cálculo de títulos públicos.

Este módulo contém apenas lógica de negócio pura, sem dependências de infraestrutura.
Dados de mercado devem ser fornecidos via MarketDataProvider.
"""
from .domain.instruments import LTN
from .domain.risk.equivalence import equivalencia

# Reexportar classes principais para compatibilidade com API legada
__all__ = [
    'LTN',
    'equivalencia',
]

# Adicionar outras classes quando implementadas
try:
    from .domain.instruments import LFT, NTNB, NTNF, DI
    if LFT:
        __all__.extend(['LFT', 'NTNB', 'NTNF', 'DI'])
except ImportError:
    pass

__version__ = "1.0.0"
