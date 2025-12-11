import pandas as pd

from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.utils import adicionar_dias_uteis
from titulospub.core.lft.calculo_lft import calcular_lft

class LFT:
    def __init__(self, data_vencimento_titulo: str, 
                       data_base: str=None, 
                       dias_liquidacao: int=1,
                       taxa: float=None,
                       quantidade=10000, 
                       cdi: float=None,  
                       feriados: list=None,
                       variaveis_mercado: VariaveisMercado | None = None):

        # Injete uma instância para evitar recriar VariaveisMercado várias vezes
        self._vm = variaveis_mercado or VariaveisMercado()

        # Variáveis globais
        self._feriados   = feriados   if feriados   is not None else self._vm.get_feriados()
        self._cdi        = cdi        if cdi        is not None else self._vm.get_cdi()

        # Datas
        self._dias_liquidacao = dias_liquidacao
        self._data_vencimento_titulo = pd.to_datetime(data_vencimento_titulo)
        self._data_base = pd.to_datetime(data_base).normalize() if data_base else pd.Timestamp.today().normalize()
        self._data_liquidacao =  adicionar_dias_uteis(data=self._data_base,
                                                           n_dias=dias_liquidacao,
                                                           feriados=self._feriados)
        
        # Quantidade de titulos
        self._quantidade = quantidade
        self._financeiro = None  # Será calculado após _calcular()
        
        # Nome
        self._nome = f"LFT {self._data_vencimento_titulo.month}/{self._data_vencimento_titulo.year}"

        # Taxa default pela ANBIMA do vencimento
        df_LFT = self._vm.get_anbimas()["LFT"]
        linha = df_LFT[df_LFT["VENCIMENTO"] == self._data_vencimento_titulo]
        if linha.empty:
            raise ValueError(f"Vencimento {self._data_vencimento_titulo.date()} não encontrado na ANBIMA.")
        self._anbima = linha.squeeze()["ANBIMA"]

        self._taxa = float(taxa) if taxa is not None else float(self._anbima)

        # Atributos DERIVADOS (serão preenchidos em _calcular)
        self._cotacao = None
        self._pu_d0 = None
        self._pu_termo = None
        self._pu_carregado = None
        

        # Calcula já na criação
        self._calcular()
        
        # Calcula o financeiro após ter o pu_d0
        self._financeiro = self._quantidade * self._pu_d0


    @property
    def taxa(self): return self._taxa
    @taxa.setter
    def taxa(self, v):
        self._taxa = float(v)
        self._calcular()
    
    @property
    def data_base(self): return self._data_base
    @data_base.setter
    def data_base(self, v):
        self._data_base = pd.to_datetime(v).normalize()
        
        self._calcular()
    
    @property
    def data_liquidacao(self): return self._data_liquidacao
    @data_liquidacao.setter
    def data_liquidacao(self, v):
        self._data_liquidacao = pd.to_datetime(v).normalize()
    
        self._calcular()
    
    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
            
        # Atualiza a quantidade
        self._quantidade = float(v)
        
        # Atualiza o financeiro baseado na nova quantidade
        self._financeiro = self._quantidade * self._pu_d0
    
    
    @property
    def dias_liquidacao(self) -> int:
        return self._dias_liquidacao
    @dias_liquidacao.setter
    def dias_liquidacao(self, n: int):
        self._dias_liquidacao = int(n)
        self._data_liquidacao = adicionar_dias_uteis(
                                                     data=self._data_base,
                                                     n_dias=self._dias_liquidacao,
                                                     feriados=self._feriados
                                                    )
        self._calcular()

    # -------- Propriedade financeiro --------
    @property
    def financeiro(self):
        return self._financeiro

    @financeiro.setter
    def financeiro(self, v):
        if v <= 0:
            raise ValueError("Financeiro deve ser maior que zero")
            
        if self._pu_d0 == 0:
            raise ValueError("PU_D0 não pode ser zero para calcular quantidade")
            
        # Calcula nova quantidade baseada no financeiro
        self._financeiro = float(v)
        self._quantidade = round(self._financeiro / self._pu_d0, 6)

    

    # -------- Método central de cálculo --------
    def _calcular(self):
        res = calcular_lft(
            data=self._data_base,
            data_liquidacao=self._data_liquidacao,
            data_vencimento=self._data_vencimento_titulo,
            taxa=self._taxa,
            cdi=self._cdi,
            feriados=self._feriados
        )
        # guarda os derivados
        self._cotacao       = res["cotacao"]
        self._pu_d0         = res["pu_d0"]
        self._pu_termo      = res["pu_termo"]
        self._pu_carregado  = res["pu_carregado"]
        
        # Atualiza o financeiro baseado na quantidade atual
        self._financeiro = self._quantidade * self._pu_d0
        
    

    # -------- Propriedades somente-leitura para derivados --------

    @property
    def cotacap(self): return self._cotacao
    @property
    def pu_d0(self): return self._pu_d0
    @property
    def pu_termo(self): return self._pu_termo
    @property
    def pu_carregado(self): return self._pu_carregado
    @property
    def dv01(self): return self._dv01
    