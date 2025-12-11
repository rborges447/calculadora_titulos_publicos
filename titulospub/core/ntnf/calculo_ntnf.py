import pandas as pd
from math import trunc

from titulospub.core.ntnf.cash_flow_ntnf import f_v_ntnf, cotacao_ntnf
from titulospub.core.auxilio import calculo_pu_carregado
from titulospub.utils import (datas_pagamento_cupons, 
                              listar_dias_entre_datas,
                              _carregar_feriados_se_necessario, 
                              _carrecar_cdi_se_necessario,
                              adicionar_dias_uteis)

def taxa_pu_ntnf(data_liquidacao: pd.Timestamp, data_vencimento: pd.Timestamp, taxa:float, feriados: pd.Series=None):

    feriados = _carregar_feriados_se_necessario(feriados)
    
    datas_cupons = datas_pagamento_cupons(data_vencimento=data_vencimento, data_liquidacao=data_liquidacao, feriados=feriados)
    

    dias = listar_dias_entre_datas(data_liquidacao=data_liquidacao, datas=datas_cupons, feriados=feriados)
    fv = f_v_ntnf(datas_cupons)
    cot = cotacao_ntnf(fv=fv, dias_entre_datas=dias, taxa=taxa)

    #Funcao de truncamento
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    return truncar(cot * 10, 6)

def calculo_dv01_ntnf(data_liquidacao: pd.Timestamp, data_vencimento: pd.Timestamp, taxa:float, feriados: pd.Series=None):
    feriados = _carregar_feriados_se_necessario(feriados)

    pu = taxa_pu_ntnf(data_liquidacao=data_liquidacao,
                      data_vencimento=data_vencimento,
                      taxa=taxa,
                      feriados=feriados)

    pu_1bp = taxa_pu_ntnf(data_liquidacao=data_liquidacao,
                      data_vencimento=data_vencimento,
                      taxa=taxa + 0.01,
                      feriados=feriados)
    
    return  pu - pu_1bp 

def calculo_carrego_ntnf(pu: float, pu_carregado: float, dv01:float):


    carrego_brl = (pu - pu_carregado) 
    carrego_bps = (pu - pu_carregado) / dv01

    return carrego_brl, carrego_bps

def calcular_ntnf(data: pd.Timestamp, data_liquidacao, data_vencimento:pd.Timestamp, taxa: float, cdi: float=None,  feriados: list=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    cdi = _carrecar_cdi_se_necessario(cdi)

    pu_d0 = taxa_pu_ntnf(data_liquidacao=data,
                         data_vencimento=data_vencimento,
                         taxa=taxa,
                         feriados=feriados)

    pu_termo = taxa_pu_ntnf(data_liquidacao=data_liquidacao,
                         data_vencimento=data_vencimento,
                         taxa=taxa,
                         feriados=feriados)
    
    dv01 = calculo_dv01_ntnf(data_liquidacao=data_liquidacao,
                            data_vencimento=data_vencimento,
                            taxa=taxa,
                            feriados=feriados)
    
    pu_carregado = calculo_pu_carregado(data=data,
                                        data_liquidacao=data_liquidacao, 
                                        pu=pu_d0, 
                                        cdi=cdi, 
                                        feriados=feriados)
    
    if data_liquidacao == data:
        data_aux = adicionar_dias_uteis(data=data, n_dias=1, feriados=feriados)
        pu_termo_real = taxa_pu_ntnf(data_liquidacao=data_aux,
                                   data_vencimento=data_vencimento,
                                   taxa=taxa,
                                   feriados=feriados)
    else:
        pu_termo_real = pu_termo
    
    # Calcula o carregamento usando o PU a termo real
    carrego_brl, carrego_bps = calculo_carrego_ntnf(
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

# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
   
    print("pu_ntnf")