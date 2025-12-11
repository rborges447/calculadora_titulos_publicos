import pandas as pd
from math import trunc

from titulospub.utils.datas import adicionar_dias_uteis, e_dia_util, dias_trabalho_total
from titulospub.utils.carregamento_var_globais import _carregar_feriados_se_necessario, _carrecar_ipca_dict_se_necessario

from titulospub.dados.ipca import inicio_fim_mes_ipca

def calculo_vna_ntnb(data: pd.Timestamp, ipca_dict: dict=None, feriados: list=None):

    feriados = _carregar_feriados_se_necessario(feriados)
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    dia_15_mes_atu = data.replace(day=15).normalize()

    # Checando se dia_15_mes_atu é dia útil, senão adiciona 1 dia útil
    if not e_dia_util(data=dia_15_mes_atu, feriados=feriados):
        dia_15_mes_atu = adicionar_dias_uteis(data=dia_15_mes_atu, n_dias=1, feriados=feriados)

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    # Definindo qual índice IPCA utilizar
    if ipca_dict["ULTIMO_MES_IPCA"] == (data - pd.DateOffset(months=1)).month and data < dia_15_mes_atu:
        vna_ntnb = truncar((ipca_dict["INDICE_IPCA_FECHADO_ANTERIOR"] / ipca_dict["INDICE_IPCA_DATA_BASE"]) * 1000, 6)
    else:
        vna_ntnb = truncar((ipca_dict["INDICE_IPCA_FECHADO_ATUAL"] / ipca_dict["INDICE_IPCA_DATA_BASE"]) * 1000, 6)

    return vna_ntnb

def calculo_vna_ajustado_ntnb(data: pd.Timestamp, data_liquidacao: pd.Timestamp, ipca_dict: dict = None, feriados: list = None, leilao=False) -> float:

    feriados = _carregar_feriados_se_necessario(feriados)
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    # Datas de início e fim do mês IPCA
    inicio_mes_ipca, fim_mes_ipca = inicio_fim_mes_ipca(data=data, feriados=feriados)

    if leilao:
        # Dias úteis passados entre início do mês IPCA e data de liquidação
        #dias_uteis_passados = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=data_liquidacao, feriados=None)
        dias_uteis_passados = abs((data_liquidacao - inicio_mes_ipca).days)

        # Dias úteis no mês IPCA
        #dias_uteis_mes_ipca = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=fim_mes_ipca, feriados=None)
        dias_uteis_mes_ipca = abs((fim_mes_ipca - inicio_mes_ipca).days)

    else:
        dias_uteis_passados = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=data_liquidacao, feriados=feriados)
        dias_uteis_mes_ipca = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=fim_mes_ipca, feriados=feriados)

    dias_uteis_passados = float(dias_uteis_passados)
    dias_uteis_mes_ipca = float(dias_uteis_mes_ipca)

    # Puxa o VNA não ajustado
    vna_ntnb = calculo_vna_ntnb(data=data, ipca_dict=ipca_dict, feriados=feriados)

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    # Calcula VNA ajustado
    vna_ntnb_ajustado = truncar(
        truncar((1 + (ipca_dict["IPCA_USADO"] / 100)) ** truncar(dias_uteis_passados / dias_uteis_mes_ipca, 14), 14) * vna_ntnb,
        6
    )

    return vna_ntnb_ajustado
'''

def calculo_vna_ajustado_ntnb(data: pd.Timestamp, data_liquidacao: pd.Timestamp, ipca_dict: dict = None, feriados: list = None) -> float:

    feriados = _carregar_feriados_se_necessario(feriados)
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    # Datas de início e fim do mês IPCA
    inicio_mes_ipca, fim_mes_ipca = inicio_fim_mes_ipca(data=data, feriados=feriados)

    # Dias úteis passados entre início do mês IPCA e data de liquidação
    dias_uteis_passados = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=data_liquidacao, feriados=feriados)

    # Dias úteis no mês IPCA
    dias_uteis_mes_ipca = dias_trabalho_total(data_inicio=inicio_mes_ipca, data_fim=fim_mes_ipca, feriados=feriados)

    dias_uteis_passados = float(dias_uteis_passados)
    dias_uteis_mes_ipca = float(dias_uteis_mes_ipca)

    # Puxa o VNA não ajustado
    vna_ntnb = calculo_vna_ntnb(data=data, ipca_dict=ipca_dict, feriados=feriados)

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    # Calcula VNA ajustado
    vna_ntnb_ajustado = truncar(
        truncar((1 + (ipca_dict["IPCA_USADO"] / 100)) ** truncar(dias_uteis_passados / dias_uteis_mes_ipca, 14), 14) * vna_ntnb,
        6
    )

    return vna_ntnb_ajustado


'''

def fator_ipca(data: pd.Timestamp, data_liquidacao: pd.Timestamp, ipca_dict: dict = None, feriados: list = None) -> float:

    feriados = _carregar_feriados_se_necessario(feriados)
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    vna_ajustado_liq = calculo_vna_ajustado_ntnb(data=data, data_liquidacao=data_liquidacao, ipca_dict=ipca_dict, feriados=feriados)
    vna_ajustado_ref = calculo_vna_ajustado_ntnb(data=data, data_liquidacao=data, ipca_dict=ipca_dict, feriados=feriados)

    return vna_ajustado_liq / vna_ajustado_ref


if __name__ == "__main__":
    print("vna_ntnb")
