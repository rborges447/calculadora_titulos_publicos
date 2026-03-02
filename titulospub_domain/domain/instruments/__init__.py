"""
Módulo de instrumentos financeiros (títulos públicos).
"""
from .base import TituloBase
from .ltn import LTN

# Importar outras classes quando implementadas
try:
    from .lft import LFT, NTNB, NTNF, DI
except ImportError:
    # Stubs temporários
    LFT = None
    NTNB = None
    NTNF = None
    DI = None

__all__ = [
    'TituloBase',
    'LTN',
]

if LFT:
    __all__.extend(['LFT', 'NTNB', 'NTNF', 'DI'])
