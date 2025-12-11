from titulospub.core.di.calculo_di import calculo_dv01_di, taxa_pu_di

import pandas as pd

from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.utils import adicionar_dias_uteis, data_vencimento_ajustada
from titulospub.core.auxilio import codigo_vencimento_bmf, vencimento_codigo_bmf


class DI:
    def __init__(self, data_vencimento: str=None,
                       codigo: str=None,
                       data_base: str=None, 
                       taxa: float=None,
                       quantidade=1, 
                       cdi: float=None,  
                       feriados: list=None,
                       variaveis_mercado: VariaveisMercado | None = None):

        # Injete uma instância para evitar recriar VariaveisMercado várias vezes
        self._vm = variaveis_mercado or VariaveisMercado()

        # Variáveis globais
        self._feriados   = feriados   if feriados   is not None else self._vm.get_feriados()
        # Datas
        self._data_base = pd.to_datetime(data_base).normalize() if data_base else pd.Timestamp.today().normalize()

        if codigo == None and data_vencimento == None:
            raise ValueError("Fornece o codigo ou vencimento")
        elif codigo == None:
            self._data_vencimento = data_vencimento_ajustada(data=pd.to_datetime(data_vencimento), feriados=self._feriados)
            self._codigo = vencimento_codigo_bmf(self._data_vencimento, "DI1")
        elif data_vencimento == None:
            self._data_vencimento = data_vencimento_ajustada(data=codigo_vencimento_bmf(codigo), feriados=self._feriados)
            self._codigo = codigo
        else:
            self._data_vencimento = data_vencimento_ajustada(data=pd.to_datetime(data_vencimento), feriados=self._feriados)
            self._codigo = codigo
        
        # Quantidade de titulos
        self._quantidade = quantidade
        self._financeiro = None  # Será calculado após _calcular()
        

        # Taxa default pela BMF do vencimento
        df_di = self._vm.get_bmf()["DI"]
        linha = df_di[df_di["DI"] == self._codigo]
        if linha.empty:
            raise ValueError(f"Vencimento {self._data_vencimento.date()} não encontrado na BMF.")
        self._ajuste = linha.squeeze()["ADJ"]

        self._taxa = float(taxa) if taxa is not None else float(self._ajuste)

        # Atributos DERIVADOS (serão preenchidos em _calcular)
        self._pu = None
        self._dv01 = None


        # Calcula já na criação
        self._calcular()
        
        # Calcula o financeiro após ter o pu
        self._financeiro = self._quantidade * self._pu


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
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
            
        # Usa 1 como padrão para a primeira atribuição
        quantidade_anterior = getattr(self, "_quantidade", 1)

        # Ajusta valores para a unidade
        self._dv01 = self._dv01 / quantidade_anterior
        # Atualiza a quantidade
        self._quantidade = float(v)
        
        # Atualiza o financeiro baseado na nova quantidade
        self._financeiro = self._quantidade * self._pu
        # Reaplica multiplicação
        self._dv01 *= self._quantidade


    # -------- Propriedade financeiro --------
    @property
    def financeiro(self):
        return self._financeiro

    @financeiro.setter
    def financeiro(self, v):
        if v <= 0:
            raise ValueError("Financeiro deve ser maior que zero")
            
        if self._pu == 0:
            raise ValueError("PU não pode ser zero para calcular quantidade")
            
        # Usa 1 como padrão para a primeira atribuição
        quantidade_anterior = getattr(self, "_quantidade", 1)

        # Ajusta valores para a unidade
        self._dv01 = self._dv01 / quantidade_anterior

        # Calcula nova quantidade baseada no financeiro
        self._financeiro = float(v)
        self._quantidade = round(self._financeiro / self._pu, 6)

        # Reaplica multiplicação
        self._dv01 *= self._quantidade

    

    # -------- Método central de cálculo --------
    def _calcular(self):
       
        # guarda os derivados
        self._pu = taxa_pu_di(taxa=self._taxa,
                              codigo=self._codigo,
                              data_liquidacao=self._data_base,
                              data_vencimento=self._data_vencimento,
                              feriados=self._feriados)
        self._dv01 = calculo_dv01_di(taxa=self._taxa,
                                     codigo=self._codigo,
                                     data_liquidacao=self._data_base,
                                     data_vencimento=self._data_vencimento,
                                     feriados=self._feriados) * self._quantidade
        # Atualiza o financeiro baseado na quantidade atual
        self._financeiro = self._quantidade * self._pu
    

    # -------- Propriedades somente-leitura para derivados --------

    @property
    def pu(self): return self._pu
    @property
    def dv01(self): return self._dv01