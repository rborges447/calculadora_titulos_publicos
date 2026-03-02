"""
Classe LFT (Letras Financeiras do Tesouro) refatorada.

NOTA: Implementação parcial - seguir padrão de LTN para completar.
"""
import pandas as pd
from typing import Optional, List
from .base import TituloBase
from ...application.ports.market_data import MarketDataProvider


class LFT(TituloBase):
    """
    Classe para cálculo e gestão de títulos LFT.
    
    TODO: Implementar seguindo padrão de LTN.
    """
    
    def __init__(
        self,
        data_vencimento_titulo: str,
        data_base: Optional[str] = None,
        dias_liquidacao: int = 1,
        taxa: Optional[float] = None,
        quantidade: float = 10000,
        cdi: Optional[float] = None,
        feriados: Optional[List] = None,
        market_data_provider: Optional[MarketDataProvider] = None
    ):
        """Inicialização básica - implementar seguindo padrão LTN."""
        raise NotImplementedError("LFT ainda não implementado completamente")


class NTNB(TituloBase):
    """TODO: Implementar NTNB seguindo padrão de LTN."""
    pass


class NTNF(TituloBase):
    """TODO: Implementar NTNF seguindo padrão de LTN."""
    pass


class DI(TituloBase):
    """TODO: Implementar DI seguindo padrão de LTN."""
    pass
