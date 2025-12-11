import pandas as pd
from math import trunc

from titulospub.utils import _carregar_feriados_se_necessario, dias_trabalho_total, data_vencimento_ajustada
from titulospub.core.auxilio import codigo_vencimento_bmf

def taxa_pu_di(taxa: float, codigo: str=None, data_liquidacao=None, data_vencimento:pd.Timestamp=None, feriados: list=None):  

    feriados = _carregar_feriados_se_necessario(feriados)  
    if data_liquidacao == None: data_liquidacao=pd.Timestamp.today().normalize()

    if codigo == None and data_vencimento == None:
        raise ValueError("Fornece o codigo ou vencimento")
    elif codigo == None:
        data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)
    elif data_vencimento == None:
        data_vencimento = data_vencimento_ajustada(data=codigo_vencimento_bmf(codigo), feriados=feriados)
    else:
        pass
        
    #Funcao de truncamento
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    # Encontrando a data de vencimento real do titulo
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)

    dias = dias_trabalho_total(data_inicio=data_liquidacao, data_fim=data_vencimento, feriados=feriados)

    pu_ltn = truncar(100000 / (((taxa / 100) + 1) ** (dias / 252)), 6)

    return pu_ltn

def calculo_dv01_di(taxa: float, codigo: str=None, data_liquidacao=None, data_vencimento:pd.Timestamp=None, feriados: list=None):
    '''
    Calcula o Dv01 da LTN ( diferenca entre um PU e o PU com 1bp. sem considerar qtds de titulos)
    '''

    feriados = _carregar_feriados_se_necessario(feriados) 

    if codigo == None and data_vencimento == None:
        raise ValueError("Fornece o codigo ou vencimento")
    elif codigo == None:
        data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)
    else:
        data_vencimento = data_vencimento_ajustada(data=codigo_vencimento_bmf(codigo), feriados=feriados)

    pu = taxa_pu_di(codigo=codigo,
                    data_liquidacao=data_liquidacao, 
                    data_vencimento=data_vencimento, 
                    taxa=taxa,
                    feriados=feriados)
    
    pu_1bp = taxa_pu_di(codigo=codigo,
                        data_liquidacao=data_liquidacao, 
                        data_vencimento=data_vencimento, 
                        taxa=taxa + 0.01,
                        feriados=feriados)
    
    return abs(pu - pu_1bp)