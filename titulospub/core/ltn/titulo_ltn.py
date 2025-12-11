import pandas as pd

from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.utils import adicionar_dias_uteis
from titulospub.core.ltn.calculo_ltn import calcular_ltn
from titulospub.core.auxilio import vencimento_codigo_bmf
from titulospub.core.di.calculo_di import calculo_dv01_di

class LTN:
    """
    Classe para cálculo e gestão de títulos LTN (Letra do Tesouro Nacional).
    
    Esta classe encapsula todos os cálculos relacionados aos títulos LTN,
    incluindo preços, DV01, carregamento e hedge DI.
    """
    
    def __init__(self, 
                 data_vencimento_titulo: str, 
                 data_base: str = None, 
                 dias_liquidacao: int = 1,
                 taxa: float = None,
                 premio: float = None,
                 di: float = None,
                 quantidade: float = 50000, 
                 cdi: float = None,  
                 feriados: list = None,
                 variaveis_mercado: VariaveisMercado = None):
        """
        Inicializa uma instância do título LTN.
        
        Args:
            data_vencimento_titulo: Data de vencimento do título
            data_base: Data base para cálculos (default: hoje)
            dias_liquidacao: Dias para liquidação (default: 1)
            taxa: Taxa de juros do título
            premio: Prêmio sobre DI
            di: Taxa DI de referência
            quantidade: Quantidade de títulos
            cdi: Taxa CDI
            feriados: Lista de feriados
            variaveis_mercado: Instância de VariaveisMercado
        """
        # Configuração inicial
        self._vm = variaveis_mercado or VariaveisMercado()
        self._feriados = feriados if feriados is not None else self._vm.get_feriados()
        self._cdi = cdi if cdi is not None else self._vm.get_cdi()
        
        # Parâmetros de entrada
        self._taxa = float(taxa) if taxa is not None else None
        self._premio = float(premio) if premio is not None else None
        self._di = float(di) if di is not None else None
        self._quantidade = float(quantidade)
        
        # Configuração de datas
        self._configurar_datas(data_vencimento_titulo, data_base, dias_liquidacao)
        
        # Configuração do título
        self._configurar_titulo()
        
        # Configuração da taxa
        self._configurar_taxa()
        
        # Configuração DI
        self._configurar_di()
        
        # Inicialização de atributos derivados
        self._inicializar_atributos_derivados()
        
        # Cálculos iniciais
        self._calcular()
        self._hedge_di = self._calcular_hedge_di()
        self._financeiro = self._quantidade * self._pu_d0

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
        self._nome = f"LTN {self._data_vencimento_titulo.month}/{self._data_vencimento_titulo.year}"
        
        # Busca taxa ANBIMA
        df_ltn = self._vm.get_anbimas()["LTN"]
        linha = df_ltn[df_ltn["VENCIMENTO"] == self._data_vencimento_titulo]
        
        if linha.empty:
            raise ValueError(f"Vencimento {self._data_vencimento_titulo.date()} não encontrado na ANBIMA.")
        
        self._anbima = linha.squeeze()["ANBIMA"]
    
    def _configurar_taxa(self):
        """Configura a taxa do título baseada nos parâmetros fornecidos."""
        if self._taxa is None:
            if (self._premio is None) or (self._di is None):
                self._taxa = float(self._anbima)
            else:
                self._taxa = float(self._di + self._premio / 100)
        else:
            self._taxa = float(self._taxa)
    
    def _inicializar_atributos_derivados(self):
        """Inicializa atributos que serão calculados posteriormente."""
        self._pu_d0 = None
        self._pu_termo = None
        self._pu_carregado = None
        self._dv01 = None
        self._carrego_brl = None
        self._carrego_bps = None
        self._hedge_di = None
        self._financeiro = None

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
        """Prêmio sobre DI."""
        return self._premio
    
    @premio.setter
    def premio(self, v):
        self._premio = float(v) if v is not None else None
        self._atualizar_taxa_premio_di()
        self._calcular()
        self._atualizar_hedge_e_financeiro()

    @property
    def di(self):
        """Taxa DI de referência."""
        return self._di
    
    @di.setter
    def di(self, v):
        self._di = float(v) if v is not None else None
        self._atualizar_taxa_premio_di()
        self._calcular()
        self._atualizar_hedge_e_financeiro()
    
    @property
    def data_base(self):
        """Data base para cálculos."""
        return self._data_base
    @data_base.setter
    def data_base(self, v):
        self._data_base = pd.to_datetime(v).normalize()
        self._calcular()
        self._atualizar_hedge_e_financeiro()
    
    @property
    def data_liquidacao(self):
        """Data de liquidação."""
        return self._data_liquidacao
    @data_liquidacao.setter
    def data_liquidacao(self, v):
        self._data_liquidacao = pd.to_datetime(v).normalize()
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
            
        # Usa 1 como padrão para a primeira atribuição
        quantidade_anterior = getattr(self, "_quantidade", 1)

        # Ajusta valores para a unidade
        self._dv01 = self._dv01 / quantidade_anterior
        self._carrego_brl = self._carrego_brl / quantidade_anterior

        # Atualiza a quantidade
        self._quantidade = float(v)
        
        # Atualiza o financeiro baseado na nova quantidade
        self._financeiro = self._quantidade * self._pu_d0

        # Reaplica multiplicação
        self._dv01 *= self._quantidade
        self._carrego_brl *= self._quantidade
        
        # Atualiza hedge DI
        self._hedge_di = self._calcular_hedge_di()

    
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
        self._calcular()
        self._atualizar_hedge_e_financeiro()

    # -------- Propriedade financeiro --------
    @property
    def financeiro(self):
        """Valor financeiro total."""
        return self._financeiro

    @financeiro.setter
    def financeiro(self, v):
        if v <= 0:
            raise ValueError("Financeiro deve ser maior que zero")
            
        if self._pu_d0 == 0:
            raise ValueError("PU_D0 não pode ser zero para calcular quantidade")
            
        # Usa 1 como padrão para a primeira atribuição
        quantidade_anterior = getattr(self, "_quantidade", 1)

        # Ajusta valores para a unidade
        self._dv01 = self._dv01 / quantidade_anterior
        self._carrego_brl = self._carrego_brl / quantidade_anterior

        # Calcula nova quantidade baseada no financeiro
        self._financeiro = float(v)
        self._quantidade = round(self._financeiro / self._pu_d0, 6)

        # Reaplica multiplicação
        self._dv01 *= self._quantidade
        self._carrego_brl *= self._quantidade
        
        # Atualiza hedge DI
        self._hedge_di = self._calcular_hedge_di()
        
        # Recalcula tudo para garantir consistência
        self._calcular()
        self._atualizar_hedge_e_financeiro()

    # ==================== MÉTODOS DE CÁLCULO ====================
    
    def _calcular(self):
        """Método principal de cálculo do título."""
        res = calcular_ltn(
            data=self._data_base,
            data_liquidacao=self._data_liquidacao,
            data_vencimento=self._data_vencimento_titulo,
            taxa=self._taxa,
            cdi=self._cdi,
            feriados=self._feriados
        )
        
        # Armazena resultados
        self._pu_d0 = res["pu_d0"]
        self._pu_termo = res["pu_termo"]
        self._pu_carregado = res["pu_carregado"]
        self._dv01 = res["dv01"] * self._quantidade
        self._carrego_brl = res["carrego_brl"] * self._quantidade
        self._carrego_bps = res["carrego_bps"]
        
        # Atualiza financeiro
        self._financeiro = self._quantidade * self._pu_d0
        
        # Calcula o hedge DI
        self._hedge_di = self._calcular_hedge_di()
    
    def _configurar_di(self):
        """Configura parâmetros relacionados ao DI."""
        self._di_ref = vencimento_codigo_bmf(
            data_vencimento=self._data_vencimento_titulo,
            prefixo="DI1"
        )
        curva_di = self._vm.get_bmf()["DI"]
        self._ajuste_di = curva_di.loc[curva_di["DI"] == self._di_ref].squeeze()["ADJ"]
        self._premio_anbima = (self._anbima - self._ajuste_di) * 100
    
    def _calcular_hedge_di(self):
        """Calcula o hedge DI para o título LTN."""
        # Para LTN: hedge_di = quantidade / 100
        # Exemplo: 50k LTN = 500 contratos DI, 100k LTN = 1000 contratos DI
        return int(self._quantidade / 100)
    
    def _atualizar_hedge_e_financeiro(self):
        """Atualiza hedge DI e financeiro após mudanças."""
        self._hedge_di = self._calcular_hedge_di()
        self._financeiro = self._quantidade * self._pu_d0
    
    def _atualizar_taxa_premio_di(self):
        """Atualiza a taxa baseada em prêmio e DI quando ambos estão definidos."""
        if self._premio is not None and self._di is not None:
            self._taxa = float(self._di + self._premio / 100)

    # ==================== PROPRIEDADES SOMENTE LEITURA ====================

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
    def ajuste_di(self):
        """Ajuste DI do título."""
        return self._ajuste_di
    @property
    def premio_anbima(self):
        """Prêmio ANBIMA em pontos base."""
        return self._premio_anbima
    @property
    def hedge_di(self):
        """Hedge DI calculado."""
        return self._hedge_di