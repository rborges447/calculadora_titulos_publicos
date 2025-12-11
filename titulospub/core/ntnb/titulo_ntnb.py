import pandas as pd

from titulospub.core.ntnb.cash_flow_ntnb import cash_flow_ntnb
from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.utils.datas import adicionar_dias_uteis
from titulospub.core.ntnb.calculo_ntnb import calculo_ntnb, calculo_taxa_pu_ntnb
from titulospub.core.ntnb.vna_ntnb import calculo_vna_ajustado_ntnb
from titulospub.core.dap.calculo_dap import calculo_financeiro_dap, dv01_dap
from titulospub.core.auxilio import vencimento_codigo_bmf
from titulospub.core.di.calculo_di import calculo_dv01_di

class NTNB:
    """
    Classe para cálculo e gestão de títulos NTN-B (Nota do Tesouro Nacional - Série B).
    
    Esta classe encapsula todos os cálculos relacionados aos títulos NTN-B,
    incluindo preços, DV01, carregamento e hedge DAP.
    """
    
    def __init__(self, data_vencimento_titulo: str, 
                       data_base: str=None, 
                       dias_liquidacao: int=1,
                       taxa: float=None,
                       premio: float=None,
                       quantidade=10000, 
                       cdi: float=None, 
                       ipca_dict: dict=None, 
                       feriados: list=None,
                       variaveis_mercado: VariaveisMercado | None = None):
        """
        Inicializa uma instância do título NTN-B.
        
        Args:
            data_vencimento_titulo: Data de vencimento do título
            data_base: Data base para cálculos (default: hoje)
            dias_liquidacao: Dias para liquidação (default: 1)
            taxa: Taxa de juros do título
            premio: Prêmio sobre DAP
            quantidade: Quantidade de títulos
            cdi: Taxa CDI
            ipca_dict: Dicionário com dados do IPCA
            feriados: Lista de feriados
            variaveis_mercado: Instância de VariaveisMercado
        """
        # Configuração inicial
        self._vm = variaveis_mercado or VariaveisMercado()
        self._feriados = feriados if feriados is not None else self._vm.get_feriados()
        self._ipca_dict = ipca_dict if ipca_dict is not None else self._vm.get_ipca_dict()
        self._cdi = cdi if cdi is not None else self._vm.get_cdi()
        
        # Parâmetros de entrada
        self._quantidade = float(quantidade)
        self._premio = float(premio) if premio is not None else None
        self._taxa = float(taxa) if taxa is not None else None
        
        # Configuração de datas
        self._configurar_datas(data_vencimento_titulo, data_base, dias_liquidacao)
        
        # Configuração do título
        self._configurar_titulo()
        
        # Configuração DAP (deve vir antes da taxa para ter acesso ao ajuste_dap)
        self._configurar_dap()
        
        # Configuração da taxa (depois do DAP para poder usar ajuste_dap)
        self._configurar_taxa()
        
        # Inicialização de atributos derivados
        self._inicializar_atributos_derivados()
        
        # Cálculos iniciais
        self._calcular()
        self._financeiro = self._quantidade * self._pu_termo

    # ==================== CONFIGURAÇÃO PRIVADA ====================
    
    def _configurar_datas(self, data_vencimento_titulo: str, data_base: str, dias_liquidacao: int):
        """Configura as datas do título."""
        self._dias_liquidacao = dias_liquidacao
        self._data_vencimento_titulo = pd.to_datetime(data_vencimento_titulo)
        self._data_base = (pd.to_datetime(data_base).normalize() 
                          if data_base 
                          else pd.Timestamp.today().normalize())
        self._data_liquidacao = adicionar_dias_uteis(
            data=self._data_base,
            n_dias=dias_liquidacao,
            feriados=self._feriados
        )
    
    def _configurar_titulo(self):
        """Configura informações básicas do título."""
        self._nome = f"NTNB {self._data_vencimento_titulo.year}"
        
        # Busca taxa ANBIMA
        df_ntnb = self._vm.get_anbimas()["NTN-B"]
        linha = df_ntnb[df_ntnb["VENCIMENTO"] == self._data_vencimento_titulo]
        
        if linha.empty:
            raise ValueError(f"Vencimento {self._data_vencimento_titulo.date()} não encontrado na ANBIMA.")
        
        self._anbima = linha.squeeze()["ANBIMA"]
        self._atualizar_vna()
    
    def _configurar_taxa(self):
        """Configura a taxa do título baseada nos parâmetros fornecidos."""
        if self._taxa is None:
            if (self._premio is None):
                self._taxa = float(self._anbima)
            else:
                # Taxa = ajuste DAP + prêmio
                self._taxa = float(self._ajuste_dap + self._premio / 100)
        else:
            self._taxa = float(self._taxa)
    
    def _configurar_dap(self):
        """Configura parâmetros relacionados ao DAP."""
        self._dap_ref = vencimento_codigo_bmf(
            data_vencimento=self._data_vencimento_titulo,
            prefixo="DAP"
        )
        curva_dap = self._vm.get_bmf()["DAP"]
        serie_adj = curva_dap.loc[curva_dap["DAP"] == self._dap_ref, "ADJ"]
        if serie_adj.empty:
            raise ValueError(f"Ajuste DAP não encontrado para {self._dap_ref}.")
        self._ajuste_dap = float(serie_adj.iloc[0])
        self._premio_anbima_dap = (self._anbima - self._ajuste_dap) * 100
    
    def _inicializar_atributos_derivados(self):
        """Inicializa atributos que serão calculados posteriormente."""
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
        self._hedge_dap = None
        self._financeiro = None
        self._vna = None
        self._vna_tesouro = None
    
    def _atualizar_vna(self):
        """Atualiza os valores de VNA."""
        self._vna = calculo_vna_ajustado_ntnb(
            data=self._data_base,
            data_liquidacao=self._data_liquidacao
        )
        self._vna_tesouro = calculo_vna_ajustado_ntnb(
            data=self._data_base,
            data_liquidacao=self._data_liquidacao,
            leilao=True
        )

    # ==================== PROPRIEDADES DE ENTRADA ====================
    
    @property
    def taxa(self):
        """Taxa de juros do título."""
        return self._taxa
    
    @taxa.setter
    def taxa(self, v):
        self._taxa = float(v)
        self._calcular()
        self._atualizar_hedge_e_financeiro()
    
    @property
    def premio(self):
        """Prêmio sobre DAP."""
        return self._premio
    
    @premio.setter
    def premio(self, v):
        self._premio = float(v) if v is not None else None
        self._atualizar_taxa_premio_dap()
        self._calcular()
        self._atualizar_hedge_e_financeiro()
    
    @property
    def data_base(self):
        """Data base para cálculos."""
        return self._data_base
    
    @data_base.setter
    def data_base(self, v):
        self._data_base = pd.to_datetime(v).normalize()
        self._atualizar_vna()
        self._calcular()
        self._atualizar_hedge_e_financeiro()
    
    @property
    def data_liquidacao(self):
        """Data de liquidação."""
        return self._data_liquidacao
    
    @data_liquidacao.setter
    def data_liquidacao(self, v):
        self._data_liquidacao = pd.to_datetime(v).normalize()
        self._atualizar_vna()
        self._calcular()
        self._atualizar_hedge_e_financeiro()
    
    @property
    def quantidade(self):
        """Quantidade de títulos."""
        return self._quantidade

    @quantidade.setter
    def quantidade(self, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        self._ajustar_valores_para_quantidade(v)
        self._hedge_dap = self._calcular_hedge_dap()

    @property
    def financeiro(self):
        """Valor financeiro total."""
        return self._financeiro

    @financeiro.setter
    def financeiro(self, v):
        if v <= 0:
            raise ValueError("Financeiro deve ser maior que zero")
        if self._pu_termo == 0:
            raise ValueError("PU_termo não pode ser zero para calcular quantidade")
        self._ajustar_valores_para_financeiro(v)
        self._hedge_dap = self._calcular_hedge_dap()
    
    @property
    def dias_liquidacao(self) -> int:
        """Dias para liquidação."""
        return self._dias_liquidacao
    
    @dias_liquidacao.setter
    def dias_liquidacao(self, n: int):
        self._dias_liquidacao = int(n)
        self._data_liquidacao = adicionar_dias_uteis(
            data=self._data_base,
            n_dias=self._dias_liquidacao,
            feriados=self._feriados
        )
        self._atualizar_vna()
        self._calcular()
        self._atualizar_hedge_e_financeiro()

    # ==================== MÉTODOS DE CÁLCULO ====================
    
    def _calcular(self):
        """Método principal de cálculo do título."""
        res = calculo_ntnb(
            data=self._data_base,
            data_liquidacao=self._data_liquidacao,
            data_vencimento=self._data_vencimento_titulo,
            taxa=self._taxa,
            cdi=self._cdi,
            ipca_dict=self._ipca_dict,
            feriados=self._feriados
        )
        
        # Armazena resultados
        self._cotacao = res["cotacao"]
        self._pu_d0 = res["pu_d0"]
        self._pu_termo = res["pu_termo"]
        self._pu_carregado = res["pu_carregado"]
        self._pu_ajustado = res["pu_ajustado"]
        self._duration = res["duration"]
        self._data_vencimento_duration = res["data_vencimento_duaration"]
        self._dias_duration = res["dias_duration"]
        self._dv01 = res["dv01"] * self._quantidade
        self._carrego_brl = res["carrego"][0] * self._quantidade
        self._carrego_bps = res["carrego"][1]
        
        # Atualiza financeiro
        self._financeiro = self._quantidade * self._pu_termo
        
        # Calcula o hedge DAP
        self._hedge_dap = self._calcular_hedge_dap()
    
    def _calcular_hedge_dap(self) -> int:
        """Calcula o hedge DAP para o título NTNB."""
        dv_dap = dv01_dap(
            taxa=self._ajuste_dap,
            codigo=self._dap_ref,
            data_liquidacao=self._data_liquidacao,
            feriados=self._feriados
        )
        return int(self._dv01 / dv_dap)
    
    def _atualizar_hedge_e_financeiro(self):
        """Atualiza hedge DAP e financeiro após mudanças."""
        self._hedge_dap = self._calcular_hedge_dap()
        self._financeiro = self._quantidade * self._pu_termo
    
    def _atualizar_taxa_premio_dap(self):
        """Atualiza a taxa baseada em prêmio quando está definido."""
        if self._premio is not None:
            self._taxa = float(self._ajuste_dap + self._premio / 100)
    
    def _ajustar_valores_para_quantidade(self, nova_quantidade):
        """Ajusta valores quando a quantidade é alterada."""
        quantidade_anterior = getattr(self, "_quantidade", 1)
        
        # Normaliza valores para unidade
        self._dv01 = self._dv01 / quantidade_anterior
        self._carrego_brl = self._carrego_brl / quantidade_anterior
        
        # Atualiza quantidade
        self._quantidade = float(nova_quantidade)
        
        # Reaplica multiplicação
        self._dv01 *= self._quantidade
        self._carrego_brl *= self._quantidade
        self._financeiro = self._quantidade * self._pu_termo
    
    def _ajustar_valores_para_financeiro(self, novo_financeiro):
        """Ajusta valores quando o financeiro é alterado."""
        quantidade_anterior = getattr(self, "_quantidade", 1)
        
        # Normaliza valores para unidade
        self._dv01 = self._dv01 / quantidade_anterior
        self._carrego_brl = self._carrego_brl / quantidade_anterior
        
        # Calcula nova quantidade
        self._financeiro = float(novo_financeiro)
        self._quantidade = round(self._financeiro / self._pu_termo, 6)
        
        # Reaplica multiplicação
        self._dv01 *= self._quantidade
        self._carrego_brl *= self._quantidade
    
    def calcular_hedge_di(self, codigo_di: str) -> int:
        """Calcula o hedge DI para um código DI informado (ex.: "DI1F32").
        Usa a DV01 do título atual e a DV01 do contrato DI especificado.
        """
        curva_di = self._vm.get_bmf()["DI"]
        serie_adj = curva_di.loc[curva_di["DI"] == codigo_di, "ADJ"]
        if serie_adj.empty:
            raise ValueError(f"Ajuste DI não encontrado para {codigo_di}.")
        ajuste_di = float(serie_adj.iloc[0])
        dv_di = calculo_dv01_di(taxa=ajuste_di, codigo=codigo_di)
        return int(self._dv01 / dv_di)
    
    def pu_vna_manual(self, vna: float=None, taxa: float=None):
        """Calcula PU usando VNA manual e taxa opcional."""
        if vna is None:
            vna = self._vna_tesouro

        if taxa is not None:
            cot = cash_flow_ntnb(
                data_vencimento=self._data_vencimento_titulo, 
                data_liquidacao=self._data_liquidacao, 
                taxa=taxa
            )["cotacao"]
            return calculo_taxa_pu_ntnb(vna_ajustado=vna, cotacao=cot)

        return calculo_taxa_pu_ntnb(vna_ajustado=vna, cotacao=self._cotacao)

    # ==================== PROPRIEDADES SOMENTE LEITURA ====================

    @property
    def cotacao(self):
        """Cotação do título."""
        return self._cotacao
    
    @property
    def pu_d0(self):
        """Preço unitário à vista."""
        return self._pu_d0
    
    @property
    def pu_termo(self):
        """Preço unitário a termo."""
        return self._pu_termo
    
    @property
    def pu_carregado(self):
        """Preço unitário carregado."""
        return self._pu_carregado
    
    @property
    def pu_ajustado(self):
        """Preço unitário ajustado."""
        return self._pu_ajustado
    
    @property
    def duration(self):
        """Duration do título."""
        return self._duration
    
    @property
    def dv01(self):
        """DV01 do título."""
        return self._dv01
    
    @property
    def carrego_brl(self):
        """Carregamento em BRL."""
        return self._carrego_brl
    
    @property
    def carrego_bps(self):
        """Carregamento em pontos base."""
        return self._carrego_bps
    
    @property
    def ajuste_dap(self):
        """Ajuste DAP do título."""
        return self._ajuste_dap
    
    @property
    def premio_anbima_dap(self):
        """Prêmio ANBIMA em pontos base para DAP."""
        return self._premio_anbima_dap
    
    @property
    def hedge_dap(self):
        """Hedge DAP calculado."""
        return self._hedge_dap
