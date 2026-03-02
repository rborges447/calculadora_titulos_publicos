"""
Cálculo de Duration e métricas relacionadas.
"""
import pandas as pd
import numpy as np
from typing import List
from ..dates import dias_trabalho_total


def calculo_duration(
    datas_cupons_ajustadas: pd.DatetimeIndex,
    data_liquidacao: pd.Timestamp,
    pv_fluxos: np.ndarray
) -> float:
    """
    Calcula duration Macaulay do título.
    
    Args:
        datas_cupons_ajustadas: Datas de pagamento dos cupons
        data_liquidacao: Data de liquidação
        pv_fluxos: Valores presentes dos fluxos
        
    Returns:
        Duration em anos
    """
    datas_fluxos = pd.to_datetime(datas_cupons_ajustadas)
    data_base = pd.to_datetime(data_liquidacao)
    tempos = (datas_fluxos - data_base).days / 365.25
    soma_pv = np.sum(pv_fluxos)
    duracao = np.sum(tempos * pv_fluxos) / soma_pv
    return duracao


def data_vencimento_duration(data_liquidacao: pd.Timestamp, duration: float) -> pd.Timestamp:
    """
    Calcula data de vencimento equivalente baseada na duration.
    
    Args:
        data_liquidacao: Data de liquidação
        duration: Duration em anos
        
    Returns:
        Data de vencimento equivalente
    """
    return data_liquidacao + pd.Timedelta(days=duration * 365.25)


def dias_uteis_duration(
    data_liquidacao: pd.Timestamp,
    data_venc_duration: pd.Timestamp,
    feriados: List
) -> int:
    """
    Calcula dias úteis entre data de liquidação e data de vencimento da duration.
    
    Args:
        data_liquidacao: Data de liquidação
        data_venc_duration: Data de vencimento da duration
        feriados: Lista de feriados
        
    Returns:
        Número de dias úteis
    """
    data_inicio_np = np.datetime64(pd.to_datetime(data_liquidacao), 'D')
    data_fim_np = np.datetime64(pd.to_datetime(data_venc_duration), 'D')
    feriados_np = np.array([np.datetime64(pd.to_datetime(f), 'D') for f in feriados])
    return np.busday_count(data_inicio_np, data_fim_np, holidays=feriados_np)
