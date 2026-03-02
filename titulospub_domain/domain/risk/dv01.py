"""
Cálculo de DV01 (sensibilidade de preço a mudança de 1bp na taxa).
"""
import pandas as pd
from typing import Optional, List
from ..pricing import (
    taxa_pu_ltn,
    taxa_pu_ntnf,
    taxa_pu_di,
    calculo_taxa_pu_ntnb,
)
from ..cashflows import cash_flow_ntnb


def calculo_dv01_ltn(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    taxa: float,
    feriados: List
) -> float:
    """
    Calcula DV01 de LTN (diferença entre PU e PU com 1bp).
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        taxa: Taxa de juros anual (%)
        feriados: Lista de feriados
        
    Returns:
        DV01 (diferença de preço para 1bp)
    """
    pu = taxa_pu_ltn(
        data=data,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa,
        feriados=feriados
    )
    
    pu_1bp = taxa_pu_ltn(
        data=data,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa + 0.01,
        feriados=feriados
    )
    
    return abs(pu - pu_1bp)


def calculo_dv01_ntnf(
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    taxa: float,
    feriados: List
) -> float:
    """
    Calcula DV01 de NTNF.
    
    Args:
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        taxa: Taxa de juros anual (%)
        feriados: Lista de feriados
        
    Returns:
        DV01
    """
    pu = taxa_pu_ntnf(
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa,
        feriados=feriados
    )

    pu_1bp = taxa_pu_ntnf(
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa + 0.01,
        feriados=feriados
    )
    
    return pu - pu_1bp


def calculo_dv01_ntnb(
    data_vencimento: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    taxa: float,
    vna_ajustado: float,
    feriados: List
) -> float:
    """
    Calcula DV01 de NTNB.
    
    Args:
        data_vencimento: Data de vencimento
        data_liquidacao: Data de liquidação
        taxa: Taxa de juros anual (%)
        vna_ajustado: VNA ajustado
        feriados: Lista de feriados
        
    Returns:
        DV01
    """
    cotacao_1 = cash_flow_ntnb(
        data_vencimento=data_vencimento,
        data_liquidacao=data_liquidacao,
        feriados=feriados,
        taxa=taxa
    )["cotacao"]
   
    cotacao_2 = cash_flow_ntnb(
        data_vencimento=data_vencimento,
        data_liquidacao=data_liquidacao,
        feriados=feriados,
        taxa=taxa + 0.01
    )["cotacao"]

    pu_1 = calculo_taxa_pu_ntnb(vna_ajustado=vna_ajustado, cotacao=cotacao_1)
    pu_2 = calculo_taxa_pu_ntnb(vna_ajustado=vna_ajustado, cotacao=cotacao_2)

    return abs(pu_1 - pu_2)


def calculo_dv01_di(
    taxa: float,
    codigo: Optional[str],
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    feriados: List
) -> float:
    """
    Calcula DV01 de contrato DI.
    
    Args:
        taxa: Taxa de juros anual (%)
        codigo: Código do contrato (opcional)
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        feriados: Lista de feriados
        
    Returns:
        DV01
    """
    pu = taxa_pu_di(
        taxa=taxa,
        codigo=codigo,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        feriados=feriados
    )
    
    pu_1bp = taxa_pu_di(
        taxa=taxa + 0.01,
        codigo=codigo,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        feriados=feriados
    )
    
    return abs(pu - pu_1bp)


def calculo_carrego(pu: float, pu_carregado: float, dv01: float) -> tuple:
    """
    Calcula carregamento em BRL e pontos base (função generalizada).
    
    Args:
        pu: Preço unitário a termo
        pu_carregado: Preço unitário carregado
        dv01: DV01 do título
        
    Returns:
        Tupla (carrego_brl, carrego_bps)
    """
    carrego_brl = pu - pu_carregado
    carrego_bps = carrego_brl / dv01 if dv01 != 0 else 0.0
    return carrego_brl, carrego_bps
