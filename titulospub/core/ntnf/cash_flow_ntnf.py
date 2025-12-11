import pandas as pd
import numpy as np


def f_v_ntnf(datas_cupons_ajustadas):
    num_cupons = len(datas_cupons_ajustadas)
    
    # Calcula o valor base do cupom
    valor_cupom = round((1.1 ** 0.5 -1) * 100, 6)
    
    # Cria um array preenchido com o valor do cupom
    fv = np.full(num_cupons, valor_cupom, dtype=np.float64)
    
    # Ajusta o último elemento para adicionar +100
    fv[-1] += 100
    
    return fv

def cotacao_ntnf(fv, dias_entre_datas, taxa):
    cot = 0
    for i in range(len(fv)):
        # Calculando o valor presente (pv) diretamente
        desconto = (taxa / 100 + 1) ** (dias_entre_datas[i] / 252)
        pv = fv[i] / desconto
        cot += pv  # Somando diretamente o valor presente
        cot = float(cot)
    return cot

# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
   
    print("cashflow_ntnf")