# Agora pode importar normalmente
from titulospub.utils.datas import adicionar_dias_uteis
from titulospub.dados.orquestrador import VariaveisMercado

from titulospub.utils import  dias_trabalho_total, _carregar_feriados_se_necessario, _carrecar_cdi_se_necessario, data_vencimento_ajustada
from titulospub.core.auxilio import calculo_pu_carregado

from math import trunc
import pandas as pd

def taxa_pu_ltn(data: pd.Timedelta, data_liquidacao, data_vencimento:pd.Timestamp, taxa: float,  feriados: list=None):  

    feriados = _carregar_feriados_se_necessario(feriados)  


    #Funcao de truncamento
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    # Encontrando a data de vencimento real do titulo
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)

    dias = dias_trabalho_total(data_inicio=data_liquidacao, data_fim=data_vencimento, feriados=feriados)

    pu_ltn = truncar(1000 / (((taxa / 100) + 1) ** (dias / 252)), 6)

    return pu_ltn

def pu_taxa_ltn(data: pd.Timedelta, data_liquidacao, data_vencimento:pd.Timestamp, pu: float,  feriados: list=None):
    feriados = _carregar_feriados_se_necessario(feriados)  


    #Funcao de truncamento
    truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

    # Encontrando a data de vencimento real do titulo
    data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)

    dias = dias_trabalho_total(data_inicio=data_liquidacao, data_fim=data_vencimento, feriados=feriados)

    taxa_ltn = truncar((((1000 / pu) ** (252 / dias)) - 1) * 100, 4)
    

    return taxa_ltn


def calculo_dv01_ltn(data: pd.Timedelta, data_liquidacao, data_vencimento:pd.Timestamp, taxa: float,  feriados: list=None):
    '''
    Calcula o Dv01 da LTN ( diferenca entre um PU e o PU com 1bp. sem considerar qtds de titulos)
    '''

    feriados = _carregar_feriados_se_necessario(feriados) 

    pu = taxa_pu_ltn(data=data, 
                     data_liquidacao=data_liquidacao, 
                     data_vencimento=data_vencimento, 
                     taxa=taxa)
    
    pu_1bp = taxa_pu_ltn(data=data, 
                     data_liquidacao=data_liquidacao, 
                     data_vencimento=data_vencimento, 
                     taxa=taxa + 0.01)
    
    return abs(pu - pu_1bp)


def calculo_carrego_ltn(pu: float, pu_carregado: float, dv01:float):


    carrego_brl = (pu - pu_carregado) 
    carrego_bps = (pu - pu_carregado) / dv01

    return carrego_brl, carrego_bps

def calcular_ltn(data: pd.Timestamp, data_liquidacao, data_vencimento:pd.Timestamp, taxa: float, cdi: float=None,  feriados: list=None):
    feriados = _carregar_feriados_se_necessario(feriados)
    cdi = _carrecar_cdi_se_necessario(cdi)

    pu_d0 = taxa_pu_ltn(data=data,
                         data_liquidacao=data,
                         data_vencimento=data_vencimento,
                         taxa=taxa,
                         feriados=feriados)

    pu_termo = taxa_pu_ltn(data=data,
                         data_liquidacao=data_liquidacao,
                         data_vencimento=data_vencimento,
                         taxa=taxa,
                         feriados=feriados)
    
    dv01 = calculo_dv01_ltn(data=data,
                            data_liquidacao=data_liquidacao,
                            data_vencimento=data_vencimento,
                            taxa=taxa,
                            feriados=feriados)
    
    pu_carregado = calculo_pu_carregado(data=data, 
                                        data_liquidacao=data_liquidacao, 
                                        pu=pu_d0, 
                                        cdi=cdi, 
                                        feriados=feriados)
    
    if data_liquidacao == data:
        data_aux = adicionar_dias_uteis(data=data, n_dias=1, feriados=feriados)
        pu_termo_real = taxa_pu_ltn(data=data,
                                   data_liquidacao=data_aux,
                                   data_vencimento=data_vencimento,
                                   taxa=taxa,
                                   feriados=feriados)
    else:
        pu_termo_real = pu_termo
    
    # Calcula o carregamento usando o PU a termo real
    carrego_brl, carrego_bps = calculo_carrego_ltn(
        pu=pu_termo_real,
        pu_carregado=pu_carregado,
        dv01=dv01
    )
    
    return {
            "pu_d0": pu_d0,
            "pu_termo": pu_termo,
            "pu_carregado": pu_carregado,
            "dv01": dv01,
            "carrego_brl": carrego_brl,
            "carrego_bps": carrego_bps
           }

# =========================
# MAIN - TESTES E EXEMPLOS
# =========================
if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime, timedelta
    
    print("=== CALCULADORA LTN - TESTES ===\n")
    
    # Dados de exemplo para teste
    data_atual = pd.Timestamp.now()
    data_liquidacao = data_atual + timedelta(days=2)  # D+2
    data_vencimento = data_atual + timedelta(days=365)  # 1 ano
    taxa_exemplo = 12.50  # 12.50% a.a.
    
    print(f"Data atual: {data_atual.strftime('%d/%m/%Y')}")
    print(f"Data liquidação: {data_liquidacao.strftime('%d/%m/%Y')}")
    print(f"Data vencimento: {data_vencimento.strftime('%d/%m/%Y')}")
    print(f"Taxa: {taxa_exemplo}% a.a.\n")
    
    try:
        # Teste 1: Cálculo do PU
        print("1. Cálculo do PU da LTN:")
        pu = taxa_pu_ltn(
            data=data_atual,
            data_liquidacao=data_liquidacao,
            data_vencimento=data_vencimento,
            taxa=taxa_exemplo
        )
        print(f"   PU = R$ {pu:.6f}\n")
        
        # Teste 2: Cálculo do DV01
        print("2. Cálculo do DV01:")
        dv01 = calculo_dv01_ltn(
            data=data_atual,
            data_liquidacao=data_liquidacao,
            data_vencimento=data_vencimento,
            taxa=taxa_exemplo
        )
        print(f"   DV01 = R$ {dv01:.6f}\n")
        
        # Teste 3: Cálculo do Carregamento
        print("3. Cálculo do Carregamento:")
        carrego_brl, carrego_bps = calculo_carrego_ltn(
            data=data_atual,
            data_liquidacao=data_liquidacao,
            data_vencimento=data_vencimento,
            taxa=taxa_exemplo
        )
        print(f"   Carregamento (R$): {carrego_brl:.6f}")
        print(f"   Carregamento (bps): {carrego_bps:.2f}\n")
        
        # Teste 4: Variação de taxas
        print("4. Variação do PU com diferentes taxas:")
        taxas_teste = [10.0, 11.0, 12.0, 13.0, 14.0]
        for taxa in taxas_teste:
            pu_teste = taxa_pu_ltn(
                data=data_atual,
                data_liquidacao=data_liquidacao,
                data_vencimento=data_vencimento,
                taxa=taxa
            )
            print(f"   Taxa {taxa:5.1f}% → PU R$ {pu_teste:.6f}")
            
    except Exception as e:
        print(f"Erro durante os testes: {e}")
        print("Verifique se todas as dependências estão disponíveis.")
    
    print("\n=== FIM DOS TESTES ===")