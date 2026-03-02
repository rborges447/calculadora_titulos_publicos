"""
Cálculos relacionados a indexação (VNA, IPCA, etc).
"""
import pandas as pd
from typing import Optional, List, Dict
from ..conventions import truncar, PRECISAO_PU, PRECISAO_FATOR
from ..dates import (
    e_dia_util,
    adicionar_dias_uteis,
    dias_trabalho_total,
    inicio_fim_mes_ipca,
)
from ..types import IPCADict


def calculo_vna_ntnb(
    data: pd.Timestamp,
    ipca_dict: IPCADict,
    feriados: List
) -> float:
    """
    Calcula VNA não ajustado de NTNB.
    
    Args:
        data: Data de referência
        ipca_dict: Dicionário com dados de IPCA
        feriados: Lista de feriados
        
    Returns:
        VNA não ajustado
    """
    dia_15_mes_atu = data.replace(day=15).normalize()

    # Checando se dia_15_mes_atu é dia útil, senão adiciona 1 dia útil
    if not e_dia_util(data=dia_15_mes_atu, feriados=feriados):
        dia_15_mes_atu = adicionar_dias_uteis(data=dia_15_mes_atu, n_dias=1, feriados=feriados)

    # Definindo qual índice IPCA utilizar
    if ipca_dict.ultimo_mes_ipca == (data - pd.DateOffset(months=1)).month and data < dia_15_mes_atu:
        vna_ntnb = truncar(
            (ipca_dict.indice_ipca_fechado_anterior / ipca_dict.indice_ipca_data_base) * 1000,
            PRECISAO_PU
        )
    else:
        vna_ntnb = truncar(
            (ipca_dict.indice_ipca_fechado_atual / ipca_dict.indice_ipca_data_base) * 1000,
            PRECISAO_PU
        )

    return vna_ntnb


def calculo_vna_ajustado_ntnb(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    ipca_dict: IPCADict,
    feriados: List,
    leilao: bool = False
) -> float:
    """
    Calcula VNA ajustado de NTNB para data de liquidação.
    
    Args:
        data: Data de referência
        data_liquidacao: Data de liquidação
        ipca_dict: Dicionário com dados de IPCA
        feriados: Lista de feriados
        leilao: Se True, usa dias corridos ao invés de dias úteis
        
    Returns:
        VNA ajustado
    """
    # Datas de início e fim do mês IPCA
    inicio_mes_ipca, fim_mes_ipca = inicio_fim_mes_ipca(data=data, feriados=feriados)

    if leilao:
        # Dias corridos passados entre início do mês IPCA e data de liquidação
        dias_uteis_passados = abs((data_liquidacao - inicio_mes_ipca).days)
        # Dias corridos no mês IPCA
        dias_uteis_mes_ipca = abs((fim_mes_ipca - inicio_mes_ipca).days)
    else:
        dias_uteis_passados = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=data_liquidacao, feriados=feriados)
        dias_uteis_mes_ipca = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=fim_mes_ipca, feriados=feriados)

    dias_uteis_passados = float(dias_uteis_passados)
    dias_uteis_mes_ipca = float(dias_uteis_mes_ipca)

    # Puxa o VNA não ajustado
    vna_ntnb = calculo_vna_ntnb(data=data, ipca_dict=ipca_dict, feriados=feriados)

    # Calcula VNA ajustado
    vna_ntnb_ajustado = truncar(
        truncar(
            (1 + (ipca_dict.ipca_usado / 100)) ** truncar(dias_uteis_passados / dias_uteis_mes_ipca, PRECISAO_FATOR),
            PRECISAO_FATOR
        ) * vna_ntnb,
        PRECISAO_PU
    )

    return vna_ntnb_ajustado


def fator_ipca(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    ipca_dict: IPCADict,
    feriados: List
) -> float:
    """
    Calcula fator de ajuste IPCA entre duas datas.
    
    Args:
        data: Data de referência
        data_liquidacao: Data de liquidação
        ipca_dict: Dicionário com dados de IPCA
        feriados: Lista de feriados
        
    Returns:
        Fator de ajuste IPCA
    """
    vna_ajustado_liq = calculo_vna_ajustado_ntnb(
        data=data,
        data_liquidacao=data_liquidacao,
        ipca_dict=ipca_dict,
        feriados=feriados
    )
    vna_ajustado_ref = calculo_vna_ajustado_ntnb(
        data=data,
        data_liquidacao=data,
        ipca_dict=ipca_dict,
        feriados=feriados
    )

    return vna_ajustado_liq / vna_ajustado_ref


def calculo_vna_ajustado_lft(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    cdi: float,
    vna_lft: float,
    feriados: List
) -> float:
    """
    Calcula VNA ajustado de LFT pela Selic/CDI.
    
    Args:
        data: Data de referência
        data_liquidacao: Data de liquidação
        cdi: Taxa CDI
        vna_lft: VNA base da LFT
        feriados: Lista de feriados
        
    Returns:
        VNA ajustado
    """
    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)
    
    vna_ajustado = vna_lft
    if liq > 0:
        i = 1
        while i <= liq:
            vna_ajustado = round(round((1 + cdi / 100) ** (1 / 252), 8) * vna_ajustado, 6)
            i = i + 1
    
    return vna_ajustado
