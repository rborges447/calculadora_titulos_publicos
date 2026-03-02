"""
Funções de cálculo consolidadas para cada tipo de título.
"""
import pandas as pd
from typing import Optional, List
from ..pricing import (
    taxa_pu_ltn,
    calculo_pu_carregado,
)
from ..risk import (
    calculo_dv01_ltn,
    calculo_carrego,
)
from ..dates import adicionar_dias_uteis


def calcular_ltn(
    data: pd.Timestamp,
    data_liquidacao: pd.Timestamp,
    data_vencimento: pd.Timestamp,
    taxa: float,
    cdi: float,
    feriados: List
) -> dict:
    """
    Calcula todos os valores para LTN.
    
    Args:
        data: Data base
        data_liquidacao: Data de liquidação
        data_vencimento: Data de vencimento
        taxa: Taxa de juros
        cdi: Taxa CDI
        feriados: Lista de feriados
        
    Returns:
        Dicionário com resultados
    """
    pu_d0 = taxa_pu_ltn(
        data=data,
        data_liquidacao=data,
        data_vencimento=data_vencimento,
        taxa=taxa,
        feriados=feriados
    )

    pu_termo = taxa_pu_ltn(
        data=data,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa,
        feriados=feriados
    )
    
    dv01 = calculo_dv01_ltn(
        data=data,
        data_liquidacao=data_liquidacao,
        data_vencimento=data_vencimento,
        taxa=taxa,
        feriados=feriados
    )
    
    pu_carregado = calculo_pu_carregado(
        data=data,
        data_liquidacao=data_liquidacao,
        pu=pu_d0,
        cdi=cdi,
        feriados=feriados
    )
    
    if data_liquidacao == data:
        data_aux = adicionar_dias_uteis(data=data, n_dias=1, feriados=feriados)
        pu_termo_real = taxa_pu_ltn(
            data=data,
            data_liquidacao=data_aux,
            data_vencimento=data_vencimento,
            taxa=taxa,
            feriados=feriados
        )
    else:
        pu_termo_real = pu_termo
    
    # Calcula o carregamento usando o PU a termo real
    carrego_brl, carrego_bps = calculo_carrego(
        pu=pu_termo_real,
        pu_carregado=pu_carregado,
        dv01=dv01
    )
    
    return {
        "pu_d0": pu_d0,
        "pu_termo": pu_termo,
        "pu_carregado": pu_carregado,
        "dv01": dv01,
        "carrego_brl": carrego_brl,
        "carrego_bps": carrego_bps
    }
