import numpy as np
import pandas as pd
from math import trunc

from titulospub.core.ntnb.cash_flow_ntnb import cash_flow_ntnb
from titulospub.core.ntnb.vna_ntnb import calculo_vna_ajustado_ntnb, fator_ipca

from titulospub.utils.datas import dias_trabalho_total, adicionar_dias_uteis
from titulospub.utils.carregamento_var_globais import (_carregar_feriados_se_necessario, 
                                                       _carrecar_ipca_dict_se_necessario,
                                                       _carrecar_cdi_se_necessario)

def calculo_duration(datas_cupons_ajustadas, data_liquidacao, pv_fluxos):
    datas_fluxos = pd.to_datetime(datas_cupons_ajustadas)
    data_base = pd.to_datetime(data_liquidacao)
    tempos = (datas_fluxos - data_base).days / 365.25
    soma_pv = np.sum(pv_fluxos)
    duracao = np.sum(tempos * pv_fluxos) / soma_pv
    return duracao

def data_vencimento_duration(data_liquidacao: pd.Timestamp, duration: float):
    return data_liquidacao + pd.Timedelta(days=duration * 365.25)

def dias_uteis_duration(data_liquidacao, data_venc_duration, feriados=None):
    feriados = _carregar_feriados_se_necessario(feriados)

    data_inicio_np = np.datetime64(pd.to_datetime(data_liquidacao), 'D')
    data_fim_np = np.datetime64(pd.to_datetime(data_venc_duration), 'D')
    feriados_np = np.array([np.datetime64(pd.to_datetime(f), 'D') for f in feriados])
    return np.busday_count(data_inicio_np, data_fim_np, holidays=feriados_np)

'''
def calculo_dv01_ntnb(duration, pu, taxa):
    return (duration * (0.01 / 100) / (1 + taxa / 100 / 2)) * pu
'''

def cauculo_pu_carregado(data, data_liquidacao, pu, cdi=None, feriados=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    cdi = _carrecar_cdi_se_necessario(cdi)

    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)

    if liq == 0:
        liq += 1

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais
    return truncar(((1 + cdi / 100) ** (liq / 252)) * pu, 6)

def calculo_pu_ajustado(data, data_liquidacao, taxa, pu, ipca_dict=None, feriados=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)

    if liq == 0:
        liq += 1
        data_liquidacao = adicionar_dias_uteis(data=data_liquidacao, n_dias=1, feriados=feriados)

    fator = fator_ipca(data=data, data_liquidacao=data_liquidacao, ipca_dict=ipca_dict, feriados=feriados)

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais
    return truncar(pu * ((1 + taxa / 100) ** (1 / 252)) * fator, 6)

def calculo_carrego_ntnb(pu_carregado, pu_ajustado, dv01):
    carrego_brl = pu_ajustado - pu_carregado  
    carrego_bps = carrego_brl / dv01
    return carrego_brl, carrego_bps

def calculo_taxa_pu_ntnb(vna_ajustado, cotacao):
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais
    return truncar(vna_ajustado * (cotacao / 100), 6)

def calculo_dv01_ntnb(data_vencimento, data_liquidacao, taxa, vna_ajustado, feriados=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    cotacao_1 = cash_flow_ntnb(data_vencimento=data_vencimento, 
                                data_liquidacao=data_liquidacao, 
                                feriados=feriados, 
                                taxa=taxa)["cotacao"]
   
    cotacao_2 = cash_flow_ntnb(data_vencimento=data_vencimento, 
    data_liquidacao=data_liquidacao, 
    feriados=feriados, 
    taxa=taxa + 0.01)["cotacao"]

    pu_1 = calculo_taxa_pu_ntnb(vna_ajustado=vna_ajustado, cotacao=cotacao_1)
    pu_2 = calculo_taxa_pu_ntnb(vna_ajustado=vna_ajustado, cotacao=cotacao_2)

    return abs(pu_1 - pu_2)   

def calculo_ntnb(data, data_liquidacao, data_vencimento, taxa, cdi=None, ipca_dict=None, feriados=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    cash_flow_d0 = cash_flow_ntnb(data_vencimento=data_vencimento, data_liquidacao=data, feriados=feriados, taxa=taxa)
    datas_cupons_d0 = cash_flow_d0["datas_pagamento_cupons"]
    pv_d0 = cash_flow_d0["pv_cupons"]
    cotacao_d0 = cash_flow_d0["cotacao"]

    cash_flow_termo = cash_flow_ntnb(data_vencimento=data_vencimento, data_liquidacao=data_liquidacao, feriados=feriados, taxa=taxa)
    datas_cupons_termo = cash_flow_termo["datas_pagamento_cupons"]
    pv_termo = cash_flow_termo["pv_cupons"]
    cotacao_termo = cash_flow_termo["cotacao"]

    vna_ajustado_d0 = calculo_vna_ajustado_ntnb(data=data, data_liquidacao=data, ipca_dict=ipca_dict, feriados=feriados, leilao=False)
    vna_ajustado_termo = calculo_vna_ajustado_ntnb(data=data, data_liquidacao=data_liquidacao, ipca_dict=ipca_dict, feriados=feriados, leilao=False)

    pu_d0 = calculo_taxa_pu_ntnb(vna_ajustado=vna_ajustado_d0, cotacao=cotacao_d0)
    pu_termo = calculo_taxa_pu_ntnb(vna_ajustado=vna_ajustado_termo, cotacao=cotacao_termo)

    duration = calculo_duration(datas_cupons_ajustadas=datas_cupons_termo, data_liquidacao=data_liquidacao, pv_fluxos=pv_termo)
    dt_venc_duration = data_vencimento_duration(data_liquidacao=data_liquidacao, duration=duration)
    duration_dias = dias_uteis_duration(data_liquidacao=data_liquidacao, data_venc_duration=dt_venc_duration, feriados=feriados)

    #dv01 = calculo_dv01_ntnb(duration=duration, pu=pu_termo, taxa=taxa)
    dv01 = calculo_dv01_ntnb(data_vencimento=data_vencimento, data_liquidacao=data_liquidacao, taxa=taxa, vna_ajustado=vna_ajustado_termo, feriados=feriados)

    pu_carregado = cauculo_pu_carregado(data=data, data_liquidacao=data_liquidacao, pu=pu_d0, cdi=cdi, feriados=feriados)
    pu_ajustado = calculo_pu_ajustado(data=data, data_liquidacao=data_liquidacao, taxa=taxa, pu=pu_d0, ipca_dict=ipca_dict, feriados=feriados)

    carrego = calculo_carrego_ntnb(pu_carregado=pu_carregado, pu_ajustado=pu_ajustado, dv01=dv01)

    return {
        "cotacao": cotacao_termo,
        "pu_d0": pu_d0,
        "pu_termo": pu_termo,
        "pu_carregado": pu_carregado,
        "pu_ajustado": pu_ajustado,
        "duration": duration,
        "data_vencimento_duaration": dt_venc_duration,
        "dias_duration": duration_dias,
        "dv01": dv01,
        "carrego": carrego
    }


if __name__ == "__main__":
    print("Calculo_ntnb")
    


