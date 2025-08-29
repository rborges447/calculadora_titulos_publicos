import pandas as pd

from titulospub.core.ntnb.cash_flow_ntnb import cash_flow_ntnb
from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.utils.datas import adicionar_dias_uteis
from titulospub.core.ntnb.calculo_ntnb import calculo_ntnb, calculo_taxa_pu_ntnb
from titulospub.core.ntnb.vna_ntnb import calculo_vna_ajustado_ntnb

class NTNB:
    def __init__(self, data_vencimento_titulo: str, 
                       data_base: str=None, 
                       dias_liquidacao: int=1,
                       taxa: float=None,
                       quantidade=10000, 
                       cdi: float=None, 
                       ipca_dict: dict=None, 
                       feriados: list=None,
                       variaveis_mercado: VariaveisMercado | None = None):

        # Injete uma instância para evitar recriar VariaveisMercado várias vezes
        self._vm = variaveis_mercado or VariaveisMercado()

        # Variáveis globais
        self._feriados   = feriados   if feriados   is not None else self._vm.get_feriados()
        self._ipca_dict  = ipca_dict  if ipca_dict  is not None else self._vm.get_ipca_dict()
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
        
        #VNA
        self._vna = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao)
        self._vna_tesouro = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao,
                                              leilao=True)

        # Nome
        self._nome = f"NTNB {self._data_vencimento_titulo.year}"

        # Taxa default pela ANBIMA do vencimento
        df_ntnb = self._vm.get_anbimas()["NTN-B"]
        linha = df_ntnb[df_ntnb["VENCIMENTO"] == self._data_vencimento_titulo]
        if linha.empty:
            raise ValueError(f"Vencimento {self._data_vencimento_titulo.date()} não encontrado na ANBIMA.")
        self._anbima = linha.squeeze()["ANBIMA"]

        self._taxa = float(taxa) if taxa is not None else float(self._anbima)

        # Atributos DERIVADOS (serão preenchidos em _calcular)
        self._cotacao = None
        self._pu_d0 = None
        self._pu_termo = None
        self._pu_carregado = None
        self._pu_ajustado = None
        self._duration = None
        self._data_vencimento_duration = None
        self._dias_duration = None
        self._dv01 = None
        self._carrego_brl = None
        self._carrego_bps = None

        # Calcula já na criação
        self._calcular()

    # -------- Propriedades gatilho (disparam recalculo) --------
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
        self._vna = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao)
        self._vna_tesouro = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao,
                                              leilao=True)
        self._calcular()
    
    @property
    def data_liquidacao(self): return self._data_liquidacao
    @data_liquidacao.setter
    def data_liquidacao(self, v):
        self._data_liquidacao = pd.to_datetime(v).normalize()
        self._vna = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao)
        self._vna_tesouro = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao,
                                              leilao=True)
        self._calcular()
    
    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, v):
        # Usa 1 como padrão para a primeira atribuição
        quantidade_anterior = getattr(self, "_quantidade", 1)

        # Ajusta valores para a unidade
        self._dv01 = self._dv01 / quantidade_anterior
        self._carrego_brl = self._carrego_brl / quantidade_anterior

        # Atualiza a quantidade
        self._quantidade = float(v)

        # Reaplica multiplicação
        self._dv01 *= self._quantidade
        self._carrego_brl *= self._quantidade

    
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
        self._vna = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao)
        self._vna_tesouro = calculo_vna_ajustado_ntnb(data=self._data_base,
                                              data_liquidacao=self._data_liquidacao,
                                              leilao=True)
        self._calcular()

    

    

    # -------- Método central de cálculo --------
    def _calcular(self):
        res = calculo_ntnb(
            data=self._data_base,
            data_liquidacao=self._data_liquidacao,
            data_vencimento=self._data_vencimento_titulo,
            taxa=self._taxa,
            cdi=self._cdi,
            ipca_dict=self._ipca_dict,
            feriados=self._feriados
        )
        # guarda os derivados
        self._cotacao       = res["cotacao"]
        self._pu_d0         = res["pu_d0"]
        self._pu_termo      = res["pu_termo"]
        self._pu_carregado  = res["pu_carregado"]
        self._pu_ajustado   = res["pu_ajustado"]
        self._duration      = res["duration"]
        self._data_vencimento_duration = res["data_vencimento_duaration"]
        self._dias_duration = res["dias_duration"]
        self._dv01          = res["dv01"] * self._quantidade
        self._carrego_brl       = res["carrego"][0]* self._quantidade
        self._carrego_bps       = res["carrego"][1]
    
    def pu_vna_manual(self, vna: float=None, taxa: float=None):
        
        if vna is None:
            vna = self._vna_tesouro

        if taxa is not None:
            cot = cash_flow_ntnb(data_vencimento=self._data_vencimento_titulo, 
                                 data_liquidacao=self._data_liquidacao, 
                                 taxa=taxa)["cotacao"]
            return calculo_taxa_pu_ntnb(vna_ajustado=vna,
                                         cotacao=cot)
        

        return calculo_taxa_pu_ntnb(vna_ajustado=vna,
                                         cotacao=self._cotacao)

    # -------- Propriedades somente-leitura para derivados --------
    @property
    def cotacao(self): return self._cotacao
    @property
    def pu_d0(self): return self._pu_d0
    @property
    def pu_termo(self): return self._pu_termo
    @property
    def pu_carregado(self): return self._pu_carregado
    @property
    def pu_ajustado(self): return self._pu_ajustado
    @property
    def duration(self): return self._duration
    @property
    def dv01(self): return self._dv01
    @property
    def carrego(self): return self._carrego
