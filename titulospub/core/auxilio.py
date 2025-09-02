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
