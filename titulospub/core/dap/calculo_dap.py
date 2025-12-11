import pandas as pd

from titulospub.dados.ipca import inicio_fim_mes_ipca
from titulospub.utils.datas import dias_trabalho_total, data_vencimento_ajustada
from titulospub.utils.carregamento_var_globais import _carrecar_ipca_dict_se_necessario, _carregar_feriados_se_necessario
from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.core.auxilio import codigo_vencimento_bmf

def dia_15_do_mes(data: pd.Timestamp) -> pd.Timestamp:
    """Retorna o dia 15 do mês e ano da data fornecida."""
    return pd.Timestamp(year=data.year, month=data.month, day=15)

def calculo_prt(data=None, ipca_dict=None):
    if data == None:
        data = pd.Timestamp.today().normalize()
    
    ipca_dict = _carrecar_ipca_dict_se_necessario(ipca_dict)

    i, f = inicio_fim_mes_ipca(pd.Timestamp.today().normalize())
    
    pro_rata = ipca_dict["INDICE_IPCA_FECHADO_ATUAL"]
    ipca_usado = ipca_dict["IPCA_USADO"]
    dias_totais = dias_trabalho_total(i,f)
    dias_passados = dias_trabalho_total(i, data)

    return round(pro_rata * ((1 + ipca_usado / 100) ** (dias_passados / dias_totais)), 2)

def calculo_pu_dap(taxa: float, codigo: str=None, data_liquidacao=None, data_vencimento:pd.Timestamp=None, feriados: list=None):
        feriados = _carregar_feriados_se_necessario(feriados)  
        if data_liquidacao == None: data_liquidacao=pd.Timestamp.today().normalize()
        
        if codigo == None and data_vencimento == None:
            raise ValueError("Fornece o codigo ou vencimento")
        elif codigo == None:
            # Já tem data_vencimento fornecida
            pass
        elif data_vencimento == None:
            # Obtém data do código
            data_vencimento = codigo_vencimento_bmf(codigo)
        else:
            # Ambos fornecidos, usa data_vencimento
            pass
        
        # Converte para o dia 15 do mês ANTES de ajustar
        data_vencimento = dia_15_do_mes(data_vencimento)
        
        # Ajusta para dia útil
        data_vencimento = data_vencimento_ajustada(data=data_vencimento, feriados=feriados)
        
        dias_uteis = dias_trabalho_total(data_liquidacao, data_vencimento)
        return 100000 / ((taxa / 100 +1) ** (dias_uteis / 252))
    
def calculo_financeiro_dap(taxa: float, codigo: str=None, data_liquidacao=None, data_vencimento:pd.Timestamp=None, feriados: list=None):
    pu = calculo_pu_dap(taxa=taxa, 
                        codigo=codigo, 
                        data_liquidacao=data_liquidacao,
                        data_vencimento=data_vencimento,
                        feriados=feriados)
    
    prt = calculo_prt(data=data_liquidacao)
    return pu * 0.00025 * prt

def dv01_dap(taxa: float, codigo: str=None, data_liquidacao=None, data_vencimento:pd.Timestamp=None, feriados: list=None):

    fin = calculo_financeiro_dap(taxa=taxa, 
                        codigo=codigo, 
                        data_liquidacao=data_liquidacao,
                        data_vencimento=data_vencimento,
                        feriados=feriados)

    fin_1bp = calculo_financeiro_dap(taxa=taxa+0.01, 
                        codigo=codigo, 
                        data_liquidacao=data_liquidacao,
                        data_vencimento=data_vencimento,
                        feriados=feriados)
    
    return abs(fin - fin_1bp)