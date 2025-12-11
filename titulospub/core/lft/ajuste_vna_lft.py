from titulospub.utils import dias_trabalho_total, _carregar_vna_lft_se_necessario,  _carrecar_cdi_se_necessario, _carregar_feriados_se_necessario
import pandas as pd

def calculo_vna_ajustado_lft(data: pd.Timestamp, data_liquidacao: pd.Timestamp, cdi: float=None, vna_lft:float=None, feriados: list=None):

    feriados = _carregar_feriados_se_necessario(feriados)
    vna_lft = _carregar_vna_lft_se_necessario(vna_lft)
    cdi = _carrecar_cdi_se_necessario(cdi)

    liq = dias_trabalho_total(data_inicio=data, data_fim=data_liquidacao, feriados=feriados)
    
    vna_ajustado = vna_lft
    if liq > 0:
        i = 1
        while i <= liq:
            vna_ajustado = round(round((1 + cdi / 100) ** (1 / 252), 8) * vna_ajustado, 6)
            i = i + 1
    else:
        pass

    
    return vna_ajustado
    
# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
    print("vna_lft")