"""
Interface para acesso a dados de mercado.

Esta interface define o contrato mínimo necessário para o domínio funcionar,
sem depender de implementações específicas de scraping/cache/banco.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import pandas as pd
from ...domain.types import IPCADict


class MarketDataProvider(ABC):
    """
    Interface para provedor de dados de mercado.
    
    Implementações podem vir de scraping, banco de dados, cache, etc.
    """
    
    @abstractmethod
    def get_feriados(self) -> List:
        """Retorna lista de feriados."""
        pass
    
    @abstractmethod
    def get_cdi(self) -> float:
        """Retorna taxa CDI."""
        pass
    
    @abstractmethod
    def get_ipca_dict(self, data: Optional[pd.Timestamp] = None) -> IPCADict:
        """
        Retorna dicionário com dados de IPCA.
        
        Args:
            data: Data de referência (opcional)
            
        Returns:
            IPCADict com dados de IPCA
        """
        pass
    
    @abstractmethod
    def get_vna_lft(self, data: Optional[pd.Timestamp] = None) -> float:
        """
        Retorna VNA base da LFT.
        
        Args:
            data: Data de referência (opcional)
            
        Returns:
            VNA base
        """
        pass
    
    @abstractmethod
    def get_anbima(self, titulo_type: str, data_vencimento: pd.Timestamp) -> float:
        """
        Retorna taxa ANBIMA para um título específico.
        
        Args:
            titulo_type: Tipo do título ("NTNB", "LTN", "LFT", "NTNF")
            data_vencimento: Data de vencimento
            
        Returns:
            Taxa ANBIMA
        """
        pass
    
    @abstractmethod
    def get_bmf_ajuste(self, tipo: str, codigo: str) -> Optional[float]:
        """
        Retorna ajuste BMF para um contrato específico.
        
        Args:
            tipo: Tipo de contrato ("DI" ou "DAP")
            codigo: Código do contrato (ex: "DI1F27", "DAPF27")
            
        Returns:
            Ajuste BMF ou None se não encontrado
        """
        pass
