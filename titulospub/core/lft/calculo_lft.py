from titulospub.core.lft.ajuste_vna_lft import calculo_vna_ajustado_lft
from titulospub.core.auxilio import calculo_pu_carregado
from titulospub.utils import (dias_trabalho_total , 
                              data_vencimento_ajustada, 
                              _carrecar_cdi_se_necessario,
                              _carregar_feriados_se_necessario,
                              _carregar_vna_lft_se_necessario)
from math import trunc
import pandas as pd



def pu_cotcao_lft(taxa: float, data_liquidacao: pd.Timestamp, data_vencimento: pd.Timestamp, feriados: pd.Series=None):

    feriados = _carregar_feriados_se_necessario(feriados)

    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)
    dias = dias_trabalho_total(data_inicio=data_liquidacao + pd.Timedelta(days=0), data_fim=data_vencimento, feriados=feriados)
    
    #Funcao de truncamento
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    cot = truncar(100 / ((taxa / 100 + 1) ** (dias / 252)), 4)
    return cot


def taxa_pu_lft(data: pd.to_datetime, data_liquidacao: pd.to_datetime, data_vencimento: pd.to_datetime, taxa: float,  
                feriados: list=None, cdi: float=None, vna_lft: float=None):

    feriados = _carregar_feriados_se_necessario(feriados)
    cdi = _carrecar_cdi_se_necessario(cdi)
    vna_lft = _carregar_vna_lft_se_necessario(vna_lft)
    
    
    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)

    #Calculando a cotacao
    cot = pu_cotcao_lft(taxa=taxa, data_liquidacao=data_liquidacao, data_vencimento=data_vencimento, feriados=feriados)

    #calculando o vna ajustado
    vna_ajustado = calculo_vna_ajustado_lft(data=data, data_liquidacao=data_liquidacao, cdi=cdi, vna_lft=vna_lft, feriados=feriados)


    #Funcao de truncamento
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    return truncar(cot * vna_ajustado / 100, 6)

def calcular_lft(data: pd.to_datetime, data_liquidacao: pd.to_datetime, data_vencimento: pd.to_datetime, taxa: float,  
                feriados: list=None, cdi: float=None, vna_lft: float=None):
    
    feriados = _carregar_feriados_se_necessario(feriados)
    cdi = _carrecar_cdi_se_necessario(cdi)

    cot = pu_cotcao_lft(taxa=taxa, data_liquidacao=data_liquidacao, data_vencimento=data_vencimento, feriados=feriados)

    pu_d0 = taxa_pu_lft(data=data,
                         data_liquidacao=data,
                         data_vencimento=data_vencimento,
                         taxa=taxa,
                         feriados=feriados)

    pu_termo = taxa_pu_lft(data=data,
                         data_liquidacao=data_liquidacao,
                         data_vencimento=data_vencimento,
                         taxa=taxa,
                         feriados=feriados)
    

    pu_carregado = calculo_pu_carregado(data=data, 
                                        data_liquidacao=data_liquidacao, 
                                        pu=pu_d0, 
                                        cdi=cdi, 
                                        feriados=feriados)
    
    return {
            "cotacao": cot,
            "pu_d0": pu_d0,
            "pu_termo": pu_termo,
            "pu_carregado": pu_carregado
            }

# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
    print("pu_lft")