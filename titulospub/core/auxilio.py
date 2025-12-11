import pandas as pd 
from math import trunc

from titulospub.utils import _carregar_feriados_se_necessario, _carrecar_cdi_se_necessario, dias_trabalho_total

def calculo_pu_carregado(data, data_liquidacao, pu, cdi=None, feriados=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    cdi = _carrecar_cdi_se_necessario(cdi)

    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)

    if liq == 0:
        liq += 1

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais
    return truncar(((1 + cdi / 100) ** (liq / 252)) * pu, 6)

def codigo_vencimento_bmf(codigo: str ):
    letras  = {"F":"01", "G":"02", "H":"03",
            "J":"04", "K":"05", "M":"06",
            "N":"07", "Q":"08", "U":"09",
            "V":"10", "X":"11", "Z":"12"}


    for k, v in letras.items():
        codigo = codigo.replace(k, v)


    dia = "01"
    mes = codigo[3:5]
    ano = str(int(codigo[5:]) + 2000)

    data_vencimento = f"{ano}-{mes}-{dia}"
    return pd.to_datetime(data_vencimento)

def vencimento_codigo_bmf(data_vencimento, prefixo):    
    letras  = {"01":"F", "02":"G", "03":"H",
                "04":"J", "05":"K", "06":"M",
                "07":"N", "08":"Q", "09":"U",
                "10":"V", "11":"X", "12":"Z"}

    dt = data_vencimento.strftime("%Y-%m-%d")
    ano = dt[2:4]
    mes = dt[5:7]


    for k, v in letras.items():
        mes = mes.replace(k, v)

    codigo = f"{prefixo}{mes}{ano}"
    return codigo