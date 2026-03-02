"""
Geração de cronogramas e datas de pagamento.
"""
from typing import Optional, List, Tuple
import numpy as np
import pandas as pd
from .calendar import (
    ajustar_para_proximo_dia_util,
    e_dia_util,
    adicionar_dias_uteis,
)


def datas_pagamento_cupons(
    data_vencimento: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    frequencia: int = 2,
    feriados: Optional[List] = None,
) -> pd.DatetimeIndex:
    """
    Gera as datas de pagamento de cupons ajustadas para dias úteis.

    Args:
        data_vencimento: Data de vencimento do título
        data_liquidacao: Data de liquidação
        frequencia: Frequência de pagamento de cupons por ano (padrão: 2 = semestral)
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        DatetimeIndex com datas de pagamento de cupons ajustadas
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    intervalo_meses = 12 // frequencia
    datas = []
    data_prox_cupom = data_vencimento
    while data_prox_cupom >= data_liquidacao:
        datas.append(data_prox_cupom)
        data_prox_cupom -= pd.DateOffset(months=intervalo_meses)
    return ajustar_para_proximo_dia_util(datas=np.array(datas[::-1]), feriados=feriados)


def inicio_fim_mes_ipca(data: pd.Timestamp, feriados: Optional[List] = None) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Calcula as datas de início e fim do mês IPCA para uma data.
    
    O mês IPCA é definido entre os dias 15 de meses consecutivos.
    
    Args:
        data: Data de referência
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)
        
    Returns:
        Tupla (inicio_mes_ipca, fim_mes_ipca)
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    # Criar dicionário com os dias 15 relevantes
    dia_15_dict = {
        "dia_15_mes_ant": (data - pd.DateOffset(months=1)).replace(day=15).normalize(),
        "dia_15_mes_atual": data.replace(day=15).normalize(),
        "dia_15_mes_prox": (data + pd.DateOffset(months=1)).replace(day=15).normalize(),
    }

    # Ajusta os dias 15 caso não sejam úteis
    for dia_15 in dia_15_dict:
        if not e_dia_util(data=dia_15_dict[dia_15], feriados=feriados):
            dia_15_dict[dia_15] = adicionar_dias_uteis(data=dia_15_dict[dia_15], n_dias=1, feriados=feriados)
    
    # Define o inicio e fim do mes IPCA
    if data < dia_15_dict["dia_15_mes_atual"]:
        inicio_mes_ipca = dia_15_dict["dia_15_mes_ant"]
        fim_mes_ipca = dia_15_dict["dia_15_mes_atual"]
    else:
        inicio_mes_ipca = dia_15_dict["dia_15_mes_atual"]
        fim_mes_ipca = dia_15_dict["dia_15_mes_prox"]
    
    return inicio_mes_ipca, fim_mes_ipca
