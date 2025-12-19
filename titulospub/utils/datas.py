from typing import List, Optional

import numpy as np
import pandas as pd

from titulospub.utils.carregamento_var_globais import _carregar_feriados_se_necessario


def adicionar_dias_uteis(
    data: pd.Timestamp, n_dias: int, feriados: Optional[List] = None
) -> pd.Timestamp:
    """
    Adiciona n dias úteis a uma data, considerando feriados.

    Args:
        data: Data base
        n_dias: Número de dias úteis a adicionar
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        Data resultante após adicionar n dias úteis
    """
    feriados = _carregar_feriados_se_necessario(feriados)
    custom_bday = pd.offsets.CustomBusinessDay(holidays=feriados)
    return data + n_dias * custom_bday


def e_dia_util(data: pd.Timestamp, feriados: Optional[List] = None) -> bool:
    """
    Verifica se uma data é dia útil (não é sábado, domingo ou feriado).

    Args:
        data: Data a verificar
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        True se for dia útil, False caso contrário
    """
    feriados = _carregar_feriados_se_necessario(feriados)
    return data.weekday() < 5 and data not in feriados


def dias_trabalho_total(
    data_inicio: pd.Timestamp, data_fim: pd.Timestamp, feriados: Optional[List] = None
) -> int:
    """
    Calcula o número total de dias úteis entre duas datas (inclusive).

    Args:
        data_inicio: Data inicial
        data_fim: Data final
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        Número de dias úteis entre as datas
    """
    feriados = _carregar_feriados_se_necessario(feriados)
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
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        Array com número de dias úteis para cada data
    """
    feriados = _carregar_feriados_se_necessario(feriados)
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
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        DatetimeIndex com datas ajustadas
    """
    feriados = _carregar_feriados_se_necessario(feriados)
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


def listar_datas(
    data_inicio: pd.Timestamp, data_fim: pd.Timestamp, feriados: Optional[List] = None
) -> List[pd.Timestamp]:
    """
    Lista todas as datas úteis entre data_inicio e data_fim (inclusive).

    Args:
        data_inicio: Data inicial
        data_fim: Data final
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        Lista de timestamps representando dias úteis
    """
    feriados = _carregar_feriados_se_necessario(feriados=feriados)
    lista_datas = []

    d = data_inicio

    while d <= data_fim:

        if e_dia_util(d, feriados):
            lista_datas.append(d)
        else:
            pass

        d = adicionar_dias_uteis(data=d, n_dias=1, feriados=feriados)

    return lista_datas


def data_vencimento_ajustada(
    data: pd.Timestamp, feriados: Optional[List] = None
) -> pd.Timestamp:
    """
    Ajusta a data de vencimento para o próximo dia útil se necessário.

    Args:
        data: Data de vencimento
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        Data ajustada para dia útil
    """
    feriados = _carregar_feriados_se_necessario(feriados)

    return (
        data
        if e_dia_util(data=data, feriados=feriados)
        else adicionar_dias_uteis(data=data, n_dias=1, feriados=feriados)
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
        feriados: Lista opcional de feriados (se None, carrega automaticamente)

    Returns:
        DatetimeIndex com datas de pagamento de cupons ajustadas
    """
    feriados = _carregar_feriados_se_necessario(feriados)

    intervalo_meses = 12 // frequencia
    datas = []
    data_prox_cupom = data_vencimento
    while data_prox_cupom >= data_liquidacao:
        datas.append(data_prox_cupom)
        data_prox_cupom -= pd.DateOffset(months=intervalo_meses)
    return ajustar_para_proximo_dia_util(datas=np.array(datas[::-1]), feriados=feriados)


# Teste local
if __name__ == "__main__":
    data_base = pd.Timestamp("2025-07-31")
    print("3 dias úteis a partir de 31/07/2025 →", adicionar_dias_uteis(data_base, 3))
