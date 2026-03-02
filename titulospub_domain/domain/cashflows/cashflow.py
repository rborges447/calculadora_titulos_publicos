"""
Cálculo de fluxos de caixa para títulos com cupons.
"""
import pandas as pd
import numpy as np
from typing import Optional, List
from ..conventions import truncar, PRECISAO_COTACAO
from ..dates import datas_pagamento_cupons, dias_trabalho_total


def fv_cupons(datas_cupons: pd.DatetimeIndex, taxa_cupom: float = 6) -> np.ndarray:
    """
    Calcula os fluxos futuros (FV) dos cupons, considerando taxa de cupom e principal.
    
    Args:
        datas_cupons: Datas de pagamento dos cupons
        taxa_cupom: Taxa de cupom anual (padrão: 6% para NTNB)
        
    Returns:
        Array com valores futuros dos cupons
    """
    num_cupons = len(datas_cupons)
    valor_cupom = round(((1 + taxa_cupom / 100) ** (taxa_cupom / 12) - 1) * 100, 6)
    fv = np.full(num_cupons, valor_cupom, dtype=np.float64)
    fv[-1] += 100
    return fv


def calcular_pv_cupons(
    datas_cupons_ajustadas: pd.DatetimeIndex,
    data_liquidacao: pd.Timestamp,
    feriados: List,
    taxa: float,
    taxa_cupom: float = 6
) -> np.ndarray:
    """
    Calcula o valor presente (PV) dos cupons.
    
    Args:
        datas_cupons_ajustadas: Datas de pagamento ajustadas
        data_liquidacao: Data de liquidação
        feriados: Lista de feriados
        taxa: Taxa de desconto
        taxa_cupom: Taxa de cupom anual
        
    Returns:
        Array com valores presentes dos cupons
    """
    cupons = fv_cupons(datas_cupons_ajustadas, taxa_cupom=taxa_cupom)
    data_inicio = np.datetime64(data_liquidacao.strftime('%Y-%m-%d'))
    datas_cupons_np = np.array([np.datetime64(d.strftime('%Y-%m-%d')) for d in datas_cupons_ajustadas])
    feriados_np = pd.to_datetime(feriados).to_numpy(dtype='datetime64[D]') if feriados is not None else None

    dias_uteis = np.busday_count(data_inicio, datas_cupons_np.astype('datetime64[D]'), holidays=feriados_np)
    anos = dias_uteis / 252
    fator_desconto = (1 + taxa / 100) ** anos
    pv = cupons / fator_desconto

    return pv


def cash_flow_ntnb(
    data_vencimento: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    taxa: float,
    feriados: List,
    taxa_cupom: float = 6,
    frequencia: int = 2
) -> dict:
    """
    Calcula o fluxo de caixa de uma NTN-B (cupom e principal), valores futuros e presentes.
    
    Args:
        data_vencimento: Data de vencimento
        data_liquidacao: Data de liquidação
        taxa: Taxa de desconto
        feriados: Lista de feriados (obrigatório)
        taxa_cupom: Taxa de cupom anual (padrão: 6%)
        frequencia: Frequência de cupons por ano (padrão: 2 = semestral)
        
    Returns:
        Dicionário com datas, FV, PV e cotação
    """
    datas_cupons = datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia=frequencia, feriados=feriados)
    fv = fv_cupons(datas_cupons, taxa_cupom=taxa_cupom)
    pv = calcular_pv_cupons(datas_cupons, data_liquidacao, feriados=feriados, taxa=taxa, taxa_cupom=taxa_cupom)

    pv_total = truncar(np.sum(pv), PRECISAO_COTACAO)

    return {
        'datas_pagamento_cupons': datas_cupons,
        'fv_cupons': fv,
        'pv_cupons': pv,
        'cotacao': pv_total
    }


def f_v_ntnf(datas_cupons_ajustadas: pd.DatetimeIndex) -> np.ndarray:
    """
    Calcula valores futuros para NTNF (cupom de 10% a.a.).
    
    Args:
        datas_cupons_ajustadas: Datas de cupons
        
    Returns:
        Array com valores futuros
    """
    num_cupons = len(datas_cupons_ajustadas)
    
    # Calcula o valor base do cupom (10% a.a. semestral)
    valor_cupom = round((1.1 ** 0.5 - 1) * 100, 6)
    
    # Cria um array preenchido com o valor do cupom
    fv = np.full(num_cupons, valor_cupom, dtype=np.float64)
    
    # Ajusta o último elemento para adicionar +100
    fv[-1] += 100
    
    return fv


def cotacao_ntnf(fv: np.ndarray, dias_entre_datas: np.ndarray, taxa: float) -> float:
    """
    Calcula cotação de NTNF baseada em valores futuros e dias úteis.
    
    Args:
        fv: Valores futuros dos cupons
        dias_entre_datas: Dias úteis até cada cupom
        taxa: Taxa de desconto
        
    Returns:
        Cotação do título
    """
    cot = 0
    for i in range(len(fv)):
        # Calculando o valor presente (pv) diretamente
        desconto = (taxa / 100 + 1) ** (dias_entre_datas[i] / 252)
        pv = fv[i] / desconto
        cot += pv
        cot = float(cot)
    return cot


def cash_flow_ntnf(
    data_vencimento: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    taxa: float,
    feriados: List
) -> dict:
    """
    Calcula fluxo de caixa para NTNF (wrapper para compatibilidade).
    """
    from ..dates import datas_pagamento_cupons, listar_dias_entre_datas
    
    datas_cupons = datas_pagamento_cupons(data_vencimento=data_vencimento, data_liquidacao=data_liquidacao, feriados=feriados)
    dias = listar_dias_entre_datas(data_liquidacao=data_liquidacao, datas=datas_cupons, feriados=feriados)
    fv = f_v_ntnf(datas_cupons)
    cot = cotacao_ntnf(fv=fv, dias_entre_datas=dias, taxa=taxa)
    
    return {
        'datas_pagamento_cupons': datas_cupons,
        'fv_cupons': fv,
        'cotacao': cot
    }
