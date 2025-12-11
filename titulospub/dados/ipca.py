from titulospub.scraping.sidra_scraping import puxar_valores_ipca_fechado
from titulospub.scraping.anbima_scraping import scrap_proj_ipca
from titulospub.utils.datas import e_dia_util, adicionar_dias_uteis
import pandas as pd
from typing import Union

def inicio_fim_mes_ipca(data: pd.Timestamp, feriados=None) -> tuple:
    # Converte feriados para numpy.datetime64[D] se não for None
    if feriados is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        feriados = vm.get_feriados()

    # Criar dicionário com os dias 15 relevantes
    dia_15_dict = {
        "dia_15_mes_ant": (data - pd.DateOffset(months=1)).replace(day=15).normalize(),
        "dia_15_mes_atual": data.replace(day=15).normalize(),
        "dia_15_mes_prox": (data + pd.DateOffset(months=1)).replace(day=15).normalize(),
    }

    # Ajusta os dias 15 caso não sejam úteis
    #Aparentemente se eu puxar o vna da net eu nao preciso utilizar o ajuste de dias uteis

    
    for dia_15 in dia_15_dict:
        if not e_dia_util(data=dia_15_dict[dia_15], feriados=feriados):
            dia_15_dict[dia_15] = adicionar_dias_uteis(data=dia_15_dict[dia_15],n_dias=1, feriados=feriados)
    
    
    #Define o inicio e fim do mes IPCA
    if data < dia_15_dict["dia_15_mes_atual"]:
        inicio_mes_ipca = dia_15_dict["dia_15_mes_ant"]
        fim_mes_ipca = dia_15_dict["dia_15_mes_atual"]
    else:
        inicio_mes_ipca = dia_15_dict["dia_15_mes_atual"]
        fim_mes_ipca = dia_15_dict["dia_15_mes_prox"]
    
    return inicio_mes_ipca, fim_mes_ipca


def dicionario_ipca(data: pd.Timestamp, ipca_fechado_df: pd.DataFrame, ipca_proj_float:float, feriados=None):

    if feriados is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        feriados = vm.get_feriados()
    
    #Checando qual o ipca utilizado na data atual
    #Calculando o dia 15 do mes atual
    dia_15_mes_atu = data.replace(day=15).normalize()

    #Checando se dia_15_mes_atu e dia util se nao for add 1 dia util
    if not e_dia_util(data=dia_15_mes_atu, feriados=feriados):
        dia_15_mes_atu = adicionar_dias_uteis(data=dia_15_mes_atu, n_dias=1, feriados=feriados)

    if int(ipca_fechado_df.iloc[2, 1][4:]) ==  (data - pd.DateOffset(months=1)).month and data < dia_15_mes_atu:
        ipca_usado = ((float(ipca_fechado_df.iloc[2, 3]) / float(ipca_fechado_df.iloc[0, 3])) - 1) * 100
    else:
        ipca_usado = ipca_proj_float
    
        ipca_usado = ipca_proj_float
 
    #Atribuindo valores Para um dicionario ipca_dict
    ipca_dict= {"ULTIMO_MES_IPCA": int(ipca_fechado_df.iloc[2, 1][4:]),
                "INDICE_IPCA_DATA_BASE": 1614.62,
                "INDICE_IPCA_FECHADO_ATUAL": float(ipca_fechado_df.iloc[2, 3]),
                "INDICE_IPCA_FECHADO_ANTERIOR": float(ipca_fechado_df.iloc[0, 3]),
                "VAR_IPCA_ATUAL": float(ipca_fechado_df.iloc[3, 3]),
                "VAR_IPCA_ANTERIOR": float(ipca_fechado_df.iloc[1, 3]),
                "IPCA_PROJ": ipca_proj_float,
                "IPCA_USADO": ipca_usado
                }

    return ipca_dict
'''
def dicionario_ipca(data, feriados=None):

    if feriados is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        feriados = vm.get_feriados()
    
    #Aplicando a função para Pxar os valores do IPCA Fechado
    ipca_fechado_df = puxar_valores_ipca_fechado()
    #Aplicando a função para puxar a projecao do IPCA
    ipca_proj_float = scrap_proj_ipca()

    #Checando qual o ipca utilizado na data atual
    #Calculando o dia 15 do mes atual
    dia_15_mes_atu = data.replace(day=15).normalize()

    #Checando se dia_15_mes_atu e dia util se nao for add 1 dia util
    if not e_dia_util(data=dia_15_mes_atu, feriados=feriados):
            dia_15_mes_atu = adicionar_dias_uteis(data=dia_15_mes_atu, n_dias=1, feriados=feriados)

    if int(ipca_fechado_df.iloc[2, 1][4:]) ==  (data - pd.DateOffset(months=1)).month and data < dia_15_mes_atu:
        ipca_usado = ((float(ipca_fechado_df.iloc[2, 3]) / float(ipca_fechado_df.iloc[0, 3])) - 1) * 100
    else:
        ipca_usado = ipca_proj_float
    
        ipca_usado = ipca_proj_float
 
    #Atribuindo valores Para um dicionario ipca_dict
    ipca_dict= {"ULTIMO_MES_IPCA": int(ipca_fechado_df.iloc[2, 1][4:]),
                "INDICE_IPCA_DATA_BASE": 1614.62,
                "INDICE_IPCA_FECHADO_ATUAL": float(ipca_fechado_df.iloc[2, 3]),
                "INDICE_IPCA_FECHADO_ANTERIOR": float(ipca_fechado_df.iloc[0, 3]),
                "VAR_IPCA_ATUAL": float(ipca_fechado_df.iloc[3, 3]),
                "VAR_IPCA_ANTERIOR": float(ipca_fechado_df.iloc[1, 3]),
                "IPCA_PROJ": ipca_proj_float,
                "IPCA_USADO": ipca_usado
                }

    return ipca_dict
'''

# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
    print("ipca_services")