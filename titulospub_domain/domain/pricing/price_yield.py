"""
Conversões entre preço (PU) e taxa (yield).
"""
import pandas as pd
from typing import Optional, List
from math import trunc
from ..conventions import truncar, PRECISAO_PU, PRECISAO_TAXA, PRECISAO_COTACAO
from ..dates import (
    dias_trabalho_total,
    data_vencimento_ajustada,
)
from ..cashflows.indexing import fator_ipca
from ..types import IPCADict


def taxa_pu_ltn(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    taxa: float,
    feriados: List
) -> float:
    """
    Converte taxa em PU para LTN.
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        taxa: Taxa de juros anual (%)
        feriados: Lista de feriados
        
    Returns:
        Preço unitário (PU)
    """
    # Encontrando a data de vencimento real do titulo
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)

    dias = dias_trabalho_total(data_inicio=data_liquidacao, data_fim=data_vencimento, feriados=feriados)

    pu_ltn = truncar(1000 / (((taxa / 100) + 1) ** (dias / 252)), PRECISAO_PU)

    return pu_ltn


def pu_taxa_ltn(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    pu: float,
    feriados: List
) -> float:
    """
    Converte PU em taxa para LTN.
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        pu: Preço unitário
        feriados: Lista de feriados
        
    Returns:
        Taxa de juros anual (%)
    """
    # Encontrando a data de vencimento real do titulo
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)

    dias = dias_trabalho_total(data_inicio=data_liquidacao, data_fim=data_vencimento, feriados=feriados)

    taxa_ltn = truncar((((1000 / pu) ** (252 / dias)) - 1) * 100, PRECISAO_TAXA)

    return taxa_ltn


def pu_cotacao_lft(
    taxa: float,
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    feriados: List
) -> float:
    """
    Calcula cotação de LFT baseada em taxa.
    
    Args:
        taxa: Taxa de juros anual (%)
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        feriados: Lista de feriados
        
    Returns:
        Cotação (%)
    """
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)
    dias = dias_trabalho_total(
        data_inicio=data_liquidacao + pd.Timedelta(days=0),
        data_fim=data_vencimento,
        feriados=feriados
    )
    
    cot = truncar(100 / ((taxa / 100 + 1) ** (dias / 252)), PRECISAO_COTACAO)
    return cot


def taxa_pu_lft(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    taxa: float,
    feriados: List,
    cdi: float,
    vna_lft: float
) -> float:
    """
    Calcula PU de LFT considerando VNA ajustado e cotação.
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        taxa: Taxa de juros anual (%)
        feriados: Lista de feriados
        cdi: Taxa CDI
        vna_lft: VNA base da LFT
        
    Returns:
        Preço unitário (PU)
    """
    from ..cashflows.indexing import calculo_vna_ajustado_lft
    
    # Calculando a cotacao
    cot = pu_cotacao_lft(taxa=taxa, data_liquidacao=data_liquidacao, data_vencimento=data_vencimento, feriados=feriados)

    # calculando o vna ajustado
    vna_ajustado = calculo_vna_ajustado_lft(
        data=data,
        data_liquidacao=data_liquidacao,
        cdi=cdi,
        vna_lft=vna_lft,
        feriados=feriados
    )

    return truncar(cot * vna_ajustado / 100, PRECISAO_PU)


def taxa_pu_ntnf(
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    taxa: float,
    feriados: List
) -> float:
    """
    Calcula PU de NTNF baseado em taxa.
    
    Args:
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        taxa: Taxa de juros anual (%)
        feriados: Lista de feriados
        
    Returns:
        Preço unitário (PU)
    """
    from ..dates import datas_pagamento_cupons, listar_dias_entre_datas
    from ..cashflows import f_v_ntnf, cotacao_ntnf
    
    datas_cupons = datas_pagamento_cupons(data_vencimento=data_vencimento, data_liquidacao=data_liquidacao, feriados=feriados)
    
    dias = listar_dias_entre_datas(data_liquidacao=data_liquidacao, datas=datas_cupons, feriados=feriados)
    fv = f_v_ntnf(datas_cupons)
    cot = cotacao_ntnf(fv=fv, dias_entre_datas=dias, taxa=taxa)

    return truncar(cot * 10, PRECISAO_PU)


def taxa_pu_di(
    taxa: float,
    codigo: Optional[str],
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    feriados: List
) -> float:
    """
    Calcula PU de contrato DI.
    
    Args:
        taxa: Taxa de juros anual (%)
        codigo: Código do contrato (opcional)
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        feriados: Lista de feriados
        
    Returns:
        Preço unitário (PU)
    """
    # Encontrando a data de vencimento real do titulo
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)

    dias = dias_trabalho_total(data_inicio=data_liquidacao, data_fim=data_vencimento, feriados=feriados)

    pu_di = truncar(100000 / (((taxa / 100) + 1) ** (dias / 252)), PRECISAO_PU)

    return pu_di


def calculo_taxa_pu_ntnb(vna_ajustado: float, cotacao: float) -> float:
    """
    Calcula PU de NTNB a partir de VNA ajustado e cotação.
    
    Args:
        vna_ajustado: VNA ajustado
        cotacao: Cotação (%)
        
    Returns:
        Preço unitário (PU)
    """
    return truncar(vna_ajustado * (cotacao / 100), PRECISAO_PU)


def calculo_pu_carregado(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    pu: float,
    cdi: float,
    feriados: List
) -> float:
    """
    Calcula PU carregado pela taxa CDI.
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        pu: Preço unitário base
        cdi: Taxa CDI
        feriados: Lista de feriados
        
    Returns:
        PU carregado
    """
    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)

    if liq == 0:
        liq += 1

    return truncar(((1 + cdi / 100) ** (liq / 252)) * pu, PRECISAO_PU)


def calculo_pu_ajustado(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    taxa: float,
    pu: float,
    ipca_dict: IPCADict,
    feriados: List
) -> float:
    """
    Calcula PU ajustado pela taxa e IPCA.
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        taxa: Taxa de juros
        pu: Preço unitário base
        ipca_dict: Dicionário com dados de IPCA
        feriados: Lista de feriados
        
    Returns:
        PU ajustado
    """
    from ..dates import adicionar_dias_uteis
    
    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)

    if liq == 0:
        liq += 1
        data_liquidacao = adicionar_dias_uteis(data=data_liquidacao, n_dias=1, feriados=feriados)

    fator = fator_ipca(data=data, data_liquidacao=data_liquidacao, ipca_dict=ipca_dict, feriados=feriados)

    return truncar(pu * ((1 + taxa / 100) ** (1 / 252)) * fator, PRECISAO_PU)
