"""
Classe LTN (Letra do Tesouro Nacional) refatorada.
"""
import pandas as pd
from typing import Optional, List
from .base import TituloBase
from ..pricing.price_yield import taxa_pu_ltn, calculo_pu_carregado
from ..risk.dv01 import calculo_dv01_ltn
from ..risk.dv01 import calculo_carrego
from ..dates.calendar import adicionar_dias_uteis
from ...application.ports.market_data import MarketDataProvider


class LTN(TituloBase):
    """
    Classe para cálculo e gestão de títulos LTN (Letra do Tesouro Nacional).
    
    Refatorada para usar domínio puro sem dependências de infraestrutura.
    """
    
    def __init__(
        self,
        data_vencimento_titulo: str,
        data_base: Optional[str] = None,
        dias_liquidacao: int = 1,
        taxa: Optional[float] = None,
        premio: Optional[float] = None,
        di: Optional[float] = None,
        quantidade: float = 50000,
        cdi: Optional[float] = None,
        feriados: Optional[List] = None,
        market_data_provider: Optional[MarketDataProvider] = None
    ):
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
            feriados: Lista de feriados (obrigatório se market_data_provider não fornecido)
            market_data_provider: Provedor de dados de mercado (opcional)
        """
        # Carrega feriados e CDI
        if market_data_provider:
            if feriados is None:
                feriados = market_data_provider.get_feriados()
            if cdi is None:
                cdi = market_data_provider.get_cdi()
        
        if feriados is None:
            raise ValueError("feriados deve ser fornecido explicitamente ou via market_data_provider")
        if cdi is None:
            raise ValueError("cdi deve ser fornecido explicitamente ou via market_data_provider")
        
        self._cdi = cdi
        self._feriados = feriados
        self._market_data_provider = market_data_provider
        
        # Parâmetros de entrada
        self._taxa = float(taxa) if taxa is not None else None
        self._premio = float(premio) if premio is not None else None
        self._di = float(di) if di is not None else None
        
        # Inicializa base
        super().__init__(
            data_vencimento_titulo=data_vencimento_titulo,
            data_base=data_base,
            dias_liquidacao=dias_liquidacao,
            quantidade=quantidade,
            feriados=feriados
        )
        
        # Configuração do título (busca ANBIMA)
        self._configurar_titulo()
        
        # Configuração da taxa
        self._configurar_taxa()
        
        # Configuração DI (pode falhar se não houver provider, mas não é crítico)
        try:
            self._configurar_di()
        except:
            self._ajuste_di = None
            self._premio_anbima = None
            self._di_ref = None
        
        # Cálculos iniciais
        self._calcular()
        self._hedge_di = self._calcular_hedge_di()
        self._financeiro = self._quantidade * self._pu_d0
    
    def _configurar_titulo(self):
        """Configura informações básicas do título."""
        self._nome = f"LTN {self._data_vencimento_titulo.month}/{self._data_vencimento_titulo.year}"
        
        # Busca taxa ANBIMA
        if self._market_data_provider:
            try:
                self._anbima = self._market_data_provider.get_anbima("LTN", self._data_vencimento_titulo)
            except:
                # Se não encontrar, usa taxa padrão se fornecida, senão erro
                if self._taxa is None:
                    raise ValueError("market_data_provider necessário para buscar taxa ANBIMA ou forneça taxa explicitamente")
                self._anbima = self._taxa
        else:
            # Se não há provider, usa taxa fornecida ou levanta erro
            if self._taxa is None:
                raise ValueError("market_data_provider necessário para buscar taxa ANBIMA ou forneça taxa explicitamente")
            self._anbima = self._taxa
    
    def _configurar_taxa(self):
        """Configura a taxa do título baseada nos parâmetros fornecidos."""
        if self._taxa is None:
            if (self._premio is None) or (self._di is None):
                self._taxa = float(self._anbima)
            else:
                self._taxa = float(self._di + self._premio / 100)
        else:
            self._taxa = float(self._taxa)
    
    def _configurar_di(self):
        """Configura parâmetros relacionados ao DI."""
        from ..auxilio import vencimento_codigo_bmf
        
        self._di_ref = vencimento_codigo_bmf(
            data_vencimento=self._data_vencimento_titulo,
            prefixo="DI1"
        )
        
        if self._market_data_provider:
            self._ajuste_di = self._market_data_provider.get_bmf_ajuste("DI", self._di_ref)
            if self._ajuste_di is None:
                # Não levanta erro, apenas marca como None
                self._premio_anbima = None
            else:
                self._premio_anbima = (self._anbima - self._ajuste_di) * 100
        else:
            self._ajuste_di = None
            self._premio_anbima = None
    
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
    
    def _calcular(self):
        """Método principal de cálculo do título."""
        from ..pricing.calculations import calcular_ltn
        
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
    
    def _calcular_hedge_di(self):
        """Calcula o hedge DI para o título LTN."""
        # Para LTN: hedge_di = quantidade / 100
        return int(self._quantidade / 100)
    
    def _atualizar_hedge_e_financeiro(self):
        """Atualiza hedge DI e financeiro após mudanças."""
        self._hedge_di = self._calcular_hedge_di()
        self._financeiro = self._quantidade * self._pu_d0
    
    def _atualizar_taxa_premio_di(self):
        """Atualiza a taxa baseada em prêmio e DI quando ambos estão definidos."""
        if self._premio is not None and self._di is not None:
            self._taxa = float(self._di + self._premio / 100)
    
    def _atualizar_data_liquidacao(self):
        """Atualiza data de liquidação baseada em dias_liquidacao."""
        self._data_liquidacao = adicionar_dias_uteis(
            data=self._data_base,
            n_dias=self._dias_liquidacao,
            feriados=self._feriados
        )
    
    def _atualizar_valores_derivados(self):
        """Atualiza valores derivados após mudanças."""
        super()._atualizar_valores_derivados()
        self._hedge_di = self._calcular_hedge_di()
    
    # Propriedades específicas
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
    
    # Propriedades somente leitura
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
    
    @property
    def taxa_anbima(self):
        """Taxa ANBIMA do título."""
        return self._anbima
