import pandas as pd
import numpy as np
from math import trunc

from titulospub.utils.carregamento_var_globais import _carregar_feriados_se_necessario
from titulospub.utils.datas import datas_pagamento_cupons
'''
def datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia=2, feriados=None):
    """
    Gera as datas de pagamento de cupons ajustadas para dias úteis.
    """
    feriados = _carregar_feriados_se_necessario(feriados)

    intervalo_meses = 12 // frequencia
    datas = []
    data_prox_cupom = data_vencimento
    while data_prox_cupom >= data_liquidacao:
        datas.append(data_prox_cupom)
        data_prox_cupom -= pd.DateOffset(months=intervalo_meses)
    return ajustar_para_proximo_dia_util(datas=np.array(datas[::-1]), feriados=feriados)
'''

def fv_cupons(datas_cupons, taxa_cupom=6):
    """
    Calcula os fluxos futuros (FV) dos cupons, considerando taxa de cupom e principal.
    """
    num_cupons = len(datas_cupons)
    valor_cupom = round(((1 + taxa_cupom / 100) ** (taxa_cupom / 12) - 1) * 100, 6)
    fv = np.full(num_cupons, valor_cupom, dtype=np.float64)
    fv[-1] += 100
    return fv


def calcular_pv_cupons(datas_cupons_ajustadas, data_liquidacao, feriados, taxa, taxa_cupom=6):
    """
    Calcula o valor presente (PV) dos cupons.
    """
    feriados = _carregar_feriados_se_necessario(feriados)

    cupons = fv_cupons(datas_cupons_ajustadas, taxa_cupom=taxa_cupom)
    data_inicio = np.datetime64(data_liquidacao.strftime('%Y-%m-%d'))
    datas_cupons_np = np.array([np.datetime64(d.strftime('%Y-%m-%d')) for d in datas_cupons_ajustadas])
    feriados_np = pd.to_datetime(feriados).to_numpy(dtype='datetime64[D]') if feriados is not None else None

    dias_uteis = np.busday_count(data_inicio, datas_cupons_np.astype('datetime64[D]'), holidays=feriados_np)
    anos = dias_uteis / 252
    fator_desconto = (1 + taxa / 100) ** anos
    pv = cupons / fator_desconto

    return pv


def cash_flow_ntnb(data_vencimento, data_liquidacao, taxa, feriados=None, taxa_cupom=6, frequencia=2):
    """
    Calcula o fluxo de caixa de uma NTN-B (cupom e principal), valores futuros e presentes.
    """
    feriados = _carregar_feriados_se_necessario(feriados)

    datas_cupons = datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia=frequencia, feriados=feriados)
    fv = fv_cupons(datas_cupons, taxa_cupom=taxa_cupom)
    pv = calcular_pv_cupons(datas_cupons, data_liquidacao, feriados=feriados, taxa=taxa, taxa_cupom=taxa_cupom)

    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais
    pv_total = truncar(np.sum(pv), 4)

    return {
        'datas_pagamento_cupons': datas_cupons,
        'fv_cupons': fv,
        'pv_cupons': pv,
        'cotacao': pv_total
    }



if __name__ == "__main__":
    # Exemplo de uso
    data_vencimento = pd.Timestamp('2028-08-15')
    data_liquidacao = pd.Timestamp('2025-07-04')
    frequencia = 2
    taxa = 7.15
    # Exemplo de feriados como lista de strings (pode ser adaptado para seu caso real)
    feriados = ['2025-01-01', '2025-04-18', '2025-05-01', '2025-09-07', '2025-10-12', '2025-11-02', '2025-11-15', '2025-12-25']
    datas_cupons = datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia)
    print("Datas de cupons:", datas_cupons)
    pv = calcular_pv_cupons(datas_cupons, data_liquidacao, feriados, taxa)
    print("Present Value dos cupons:", pv)