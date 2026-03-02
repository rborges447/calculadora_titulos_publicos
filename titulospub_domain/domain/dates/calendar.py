"""
Funções de manipulação de calendário e datas úteis.

Este módulo contém apenas lógica de calendário, sem carregamento automático de dados.
Todas as funções recebem feriados como parâmetro explícito.
"""
from typing import List, Optional
import numpy as np
import pandas as pd


def adicionar_dias_uteis(
    data: pd.Timestamp, n_dias: int, feriados: Optional[List] = None
) -> pd.Timestamp:
    """
    Adiciona n dias úteis a uma data, considerando feriados.

    Args:
        data: Data base
        n_dias: Número de dias úteis a adicionar
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        Data resultante após adicionar n dias úteis
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    custom_bday = pd.offsets.CustomBusinessDay(holidays=feriados)
    return data + n_dias * custom_bday


def e_dia_util(data: pd.Timestamp, feriados: Optional[List] = None) -> bool:
    """
    Verifica se uma data é dia útil (não é sábado, domingo ou feriado).

    Args:
        data: Data a verificar
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        True se for dia útil, False caso contrário
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    return data.weekday() < 5 and data not in feriados


def dias_trabalho_total(
    data_inicio: pd.Timestamp, data_fim: pd.Timestamp, feriados: Optional[List] = None
) -> int:
    """
    Calcula o número total de dias úteis entre duas datas (inclusive).

    Args:
        data_inicio: Data inicial
        data_fim: Data final
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        Número de dias úteis entre as datas
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    data_inicio_str = data_inicio.strftime("%Y-%m-%d")
    data_fim_str = data_fim.strftime("%Y-%m-%d")
    feriados_str = pd.to_datetime(feriados).strftime("%Y-%m-%d").tolist()

    dias_uteis = np.busday_count(data_inicio_str, data_fim_str, holidays=feriados_str)
    if np.is_busday(data_inicio_str, holidays=feriados_str):
        dias_uteis += 1
    return dias_uteis - 1


def listar_dias_entre_datas(
    data_liquidacao: pd.Timestamp, datas: np.ndarray, feriados: Optional[List] = None
) -> np.ndarray:
    """
    Lista os dias úteis entre a data de liquidação e cada data fornecida.

    Args:
        data_liquidacao: Data de liquidação
        datas: Array de datas
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        Array com número de dias úteis para cada data
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    data_inicio = data_liquidacao + pd.Timedelta(days=1)
    return np.array(
        [
            dias_trabalho_total(data_inicio - pd.Timedelta(days=1), data_fim, feriados)
            for data_fim in datas
        ]
    )


def ajustar_para_proximo_dia_util(
    datas: np.ndarray, feriados: Optional[List] = None
) -> pd.DatetimeIndex:
    """
    Ajusta cada data para o próximo dia útil se não for dia útil.

    Args:
        datas: Array de datas a ajustar
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        DatetimeIndex com datas ajustadas
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    datas_ajustadas = []
    for data in datas:
        if e_dia_util(data, feriados):
            datas_ajustadas.append(data)
        else:
            data_ajustada = data
            while not e_dia_util(data_ajustada, feriados):
                data_ajustada += pd.Timedelta(days=1)
            datas_ajustadas.append(data_ajustada)
    return pd.to_datetime(datas_ajustadas)


def data_vencimento_ajustada(
    data: pd.Timestamp, feriados: Optional[List] = None
) -> pd.Timestamp:
    """
    Ajusta a data de vencimento para o próximo dia útil se necessário.

    Args:
        data: Data de vencimento
        feriados: Lista de feriados (obrigatório, não carrega automaticamente)

    Returns:
        Data ajustada para dia útil
    """
    if feriados is None:
        raise ValueError("feriados deve ser fornecido explicitamente")
    
    return (
        data
        if e_dia_util(data=data, feriados=feriados)
        else adicionar_dias_uteis(data=data, n_dias=1, feriados=feriados)
    )
