"""
Classe base para todos os títulos públicos.

Consolida código comum entre diferentes tipos de títulos.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from ..dates import (
    adicionar_dias_uteis,
    data_vencimento_ajustada,
)


class TituloBase(ABC):
    """
    Classe base abstrata para títulos públicos.
    
    Define interface comum e métodos compartilhados.
    """
    
    def __init__(
        self,
        data_vencimento_titulo: str,
        data_base: Optional[str] = None,
        dias_liquidacao: int = 1,
        quantidade: float = 10000,
        feriados: Optional[List] = None
    ):
        """
        Inicializa título base.
        
        Args:
            data_vencimento_titulo: Data de vencimento do título
            data_base: Data base para cálculos (default: hoje)
            dias_liquidacao: Dias para liquidação (default: 1)
            quantidade: Quantidade de títulos
            feriados: Lista de feriados (obrigatório)
        """
        if feriados is None:
            raise ValueError("feriados deve ser fornecido explicitamente")
        
        # Configuração de datas (método comum)
        self._configurar_datas(data_vencimento_titulo, data_base, dias_liquidacao, feriados)
        
        # Quantidade
        self._quantidade = float(quantidade)
        self._financeiro = None
        
        # Atributos derivados (serão preenchidos em _calcular)
        self._inicializar_atributos_derivados()
    
    def _configurar_datas(
        self,
        data_vencimento_titulo: str,
        data_base: Optional[str],
        dias_liquidacao: int,
        feriados: List
    ):
        """Configura as datas do título (método comum a todos)."""
        self._dias_liquidacao = dias_liquidacao
        self._data_vencimento_titulo = pd.to_datetime(data_vencimento_titulo)
        self._data_base = (
            pd.to_datetime(data_base).normalize()
            if data_base
            else pd.Timestamp.today().normalize()
        )
        self._data_liquidacao = adicionar_dias_uteis(
            data=self._data_base,
            n_dias=dias_liquidacao,
            feriados=feriados
        )
    
    @abstractmethod
    def _inicializar_atributos_derivados(self):
        """Inicializa atributos derivados específicos do título."""
        pass
    
    @abstractmethod
    def _calcular(self):
        """Método principal de cálculo (deve ser implementado por cada título)."""
        pass
    
    def _ajustar_valores_para_quantidade(self, nova_quantidade: float):
        """
        Ajusta valores quando a quantidade é alterada (método comum).
        
        Args:
            nova_quantidade: Nova quantidade
        """
        quantidade_anterior = getattr(self, "_quantidade", 1)
        
        # Normaliza valores para unidade
        if hasattr(self, "_dv01") and self._dv01 is not None:
            self._dv01 = self._dv01 / quantidade_anterior
        if hasattr(self, "_carrego_brl") and self._carrego_brl is not None:
            self._carrego_brl = self._carrego_brl / quantidade_anterior
        
        # Atualiza quantidade
        self._quantidade = float(nova_quantidade)
        
        # Reaplica multiplicação
        if hasattr(self, "_dv01") and self._dv01 is not None:
            self._dv01 *= self._quantidade
        if hasattr(self, "_carrego_brl") and self._carrego_brl is not None:
            self._carrego_brl *= self._quantidade
        
        # Atualiza financeiro
        pu_ref = getattr(self, "_pu_termo", None) or getattr(self, "_pu_d0", None)
        if pu_ref is not None:
            self._financeiro = self._quantidade * pu_ref
    
    def _ajustar_valores_para_financeiro(self, novo_financeiro: float):
        """
        Ajusta valores quando o financeiro é alterado (método comum).
        
        Args:
            novo_financeiro: Novo valor financeiro
        """
        quantidade_anterior = getattr(self, "_quantidade", 1)
        
        # Normaliza valores para unidade
        if hasattr(self, "_dv01") and self._dv01 is not None:
            self._dv01 = self._dv01 / quantidade_anterior
        if hasattr(self, "_carrego_brl") and self._carrego_brl is not None:
            self._carrego_brl = self._carrego_brl / quantidade_anterior
        
        # Calcula nova quantidade
        pu_ref = getattr(self, "_pu_termo", None) or getattr(self, "_pu_d0", None)
        if pu_ref is None or pu_ref == 0:
            raise ValueError("PU não pode ser zero para calcular quantidade")
        
        self._financeiro = float(novo_financeiro)
        self._quantidade = round(self._financeiro / pu_ref, 6)
        
        # Reaplica multiplicação
        if hasattr(self, "_dv01") and self._dv01 is not None:
            self._dv01 *= self._quantidade
        if hasattr(self, "_carrego_brl") and self._carrego_brl is not None:
            self._carrego_brl *= self._quantidade
    
    @property
    def quantidade(self) -> float:
        """Quantidade de títulos."""
        return self._quantidade
    
    @quantidade.setter
    def quantidade(self, v: float):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        self._ajustar_valores_para_quantidade(v)
        self._atualizar_valores_derivados()
    
    @property
    def financeiro(self) -> float:
        """Valor financeiro total."""
        return self._financeiro if self._financeiro is not None else self._quantidade * (getattr(self, "_pu_termo", None) or getattr(self, "_pu_d0", 0))
    
    @financeiro.setter
    def financeiro(self, v: float):
        if v <= 0:
            raise ValueError("Financeiro deve ser maior que zero")
        self._ajustar_valores_para_financeiro(v)
        self._atualizar_valores_derivados()
    
    @property
    def data_base(self) -> pd.Timestamp:
        """Data base para cálculos."""
        return self._data_base
    
    @data_base.setter
    def data_base(self, v):
        self._data_base = pd.to_datetime(v).normalize()
        self._atualizar_data_liquidacao()
        self._calcular()
        self._atualizar_valores_derivados()
    
    @property
    def data_liquidacao(self) -> pd.Timestamp:
        """Data de liquidação."""
        return self._data_liquidacao
    
    @data_liquidacao.setter
    def data_liquidacao(self, v):
        self._data_liquidacao = pd.to_datetime(v).normalize()
        self._calcular()
        self._atualizar_valores_derivados()
    
    @property
    def dias_liquidacao(self) -> int:
        """Dias para liquidação."""
        return self._dias_liquidacao
    
    @dias_liquidacao.setter
    def dias_liquidacao(self, n: int):
        self._dias_liquidacao = int(n)
        self._atualizar_data_liquidacao()
        self._calcular()
        self._atualizar_valores_derivados()
    
    def _atualizar_data_liquidacao(self):
        """Atualiza data de liquidação baseada em dias_liquidacao."""
        # Precisa de feriados - será fornecido pelas subclasses
        pass
    
    def _atualizar_valores_derivados(self):
        """Atualiza valores derivados após mudanças (pode ser sobrescrito)."""
        pu_ref = getattr(self, "_pu_termo", None) or getattr(self, "_pu_d0", None)
        if pu_ref is not None:
            self._financeiro = self._quantidade * pu_ref
