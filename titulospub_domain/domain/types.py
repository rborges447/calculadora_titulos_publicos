"""
Tipos e estruturas de dados do domínio.
"""
from typing import Dict, Optional, List
from dataclasses import dataclass
import pandas as pd


@dataclass
class IPCADict:
    """Estrutura de dados para informações de IPCA."""
    ultimo_mes_ipca: int
    indice_ipca_data_base: float = 1614.62
    indice_ipca_fechado_atual: float
    indice_ipca_fechado_anterior: float
    var_ipca_atual: float
    var_ipca_anterior: float
    ipca_proj: float
    ipca_usado: float
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'IPCADict':
        """Cria IPCADict a partir de dicionário legado."""
        return cls(
            ultimo_mes_ipca=d["ULTIMO_MES_IPCA"],
            indice_ipca_data_base=d.get("INDICE_IPCA_DATA_BASE", 1614.62),
            indice_ipca_fechado_atual=d["INDICE_IPCA_FECHADO_ATUAL"],
            indice_ipca_fechado_anterior=d["INDICE_IPCA_FECHADO_ANTERIOR"],
            var_ipca_atual=d["VAR_IPCA_ATUAL"],
            var_ipca_anterior=d["VAR_IPCA_ANTERIOR"],
            ipca_proj=d["IPCA_PROJ"],
            ipca_usado=d["IPCA_USADO"]
        )
    
    def to_dict(self) -> Dict:
        """Converte para dicionário no formato legado."""
        return {
            "ULTIMO_MES_IPCA": self.ultimo_mes_ipca,
            "INDICE_IPCA_DATA_BASE": self.indice_ipca_data_base,
            "INDICE_IPCA_FECHADO_ATUAL": self.indice_ipca_fechado_atual,
            "INDICE_IPCA_FECHADO_ANTERIOR": self.indice_ipca_fechado_anterior,
            "VAR_IPCA_ATUAL": self.var_ipca_atual,
            "VAR_IPCA_ANTERIOR": self.var_ipca_anterior,
            "IPCA_PROJ": self.ipca_proj,
            "IPCA_USADO": self.ipca_usado
        }


@dataclass
class CashFlowResult:
    """Resultado de cálculo de fluxo de caixa."""
    datas_pagamento_cupons: pd.DatetimeIndex
    fv_cupons: List[float]
    pv_cupons: List[float]
    cotacao: float
