"""
Carteira de títulos LFT.

Gerencia múltiplos vencimentos de LFT, permitindo ajustar parâmetros
individuais sem recalcular todos os títulos.
"""

from typing import Dict, List, Optional
from datetime import datetime

from titulospub.core.lft.titulo_lft import LFT
from titulospub.dados.orquestrador import VariaveisMercado
from titulospub.dados.vencimentos import get_vencimentos_lft


class CarteiraLFT:
    """
    Carteira de títulos LFT.
    
    Armazena todos os vencimentos disponíveis e permite ajustar
    parâmetros específicos de cada vencimento.
    """
    
    def __init__(
        self,
        data_base: Optional[str] = None,
        dias_liquidacao: int = 1,
        quantidade_padrao: float = 10000,
        variaveis_mercado: Optional[VariaveisMercado] = None,
    ):
        """
        Inicializa a carteira LFT.
        
        Args:
            data_base: Data base para cálculos (default: hoje)
            dias_liquidacao: Dias para liquidação (default: 1)
            quantidade_padrao: Quantidade padrão para cada título
            variaveis_mercado: Instância compartilhada de VariaveisMercado
        """
        self._vm = variaveis_mercado or VariaveisMercado()
        self._data_base = data_base
        self._dias_liquidacao = dias_liquidacao
        self._quantidade_padrao = quantidade_padrao
        
        # Dicionário de títulos: {vencimento: LFT}
        self._titulos: Dict[str, LFT] = {}
        
        # Carrega vencimentos disponíveis
        self._carregar_vencimentos()
    
    def _carregar_vencimentos(self):
        """Carrega todos os vencimentos disponíveis."""
        vencimentos = get_vencimentos_lft()
        
        for vencimento in vencimentos:
            try:
                titulo = LFT(
                    data_vencimento_titulo=vencimento,
                    data_base=self._data_base,
                    dias_liquidacao=self._dias_liquidacao,
                    quantidade=self._quantidade_padrao,
                    variaveis_mercado=self._vm,
                )
                self._titulos[vencimento] = titulo
            except Exception as e:
                print(f"[WARN] Erro ao carregar LFT {vencimento}: {e}")
                continue
    
    def atualizar_dias_liquidacao(self, dias: int):
        """
        Atualiza dias de liquidação para todos os títulos.
        
        Args:
            dias: Novo número de dias para liquidação
        """
        self._dias_liquidacao = dias
        for titulo in self._titulos.values():
            titulo.dias_liquidacao = dias
    
    def atualizar_quantidade(self, vencimento: str, quantidade: float):
        """
        Atualiza a quantidade de um título específico.
        
        Args:
            vencimento: Data de vencimento (YYYY-MM-DD)
            quantidade: Nova quantidade
        """
        if vencimento not in self._titulos:
            raise ValueError(f"Vencimento {vencimento} não encontrado na carteira")
        
        self._titulos[vencimento].quantidade = quantidade
    
    def obter_titulo(self, vencimento: str):
        """
        Obtém um título específico.
        
        Args:
            vencimento: Data de vencimento (YYYY-MM-DD)
        
        Returns:
            Instância do título LFT ou None se não encontrado
        """
        return self._titulos.get(vencimento)
    
    def obter_dados_tabela(self) -> List[Dict]:
        """
        Obtém dados de todos os títulos em formato de lista para tabela.
        
        Returns:
            Lista de dicionários com dados dos títulos
        """
        dados = []
        
        for vencimento, titulo in sorted(self._titulos.items()):
            dados.append({
                "vencimento": vencimento,
                "pu_termo": titulo.pu_termo if titulo.pu_termo else None,
                "pu_d0": titulo.pu_d0 if titulo.pu_d0 else None,
                "quantidade": titulo.quantidade,
                "financeiro": titulo.financeiro if titulo.financeiro else None,
            })
        
        return dados
    
    def obter_dados_dict(self) -> Dict[str, Dict]:
        """
        Obtém dados de todos os títulos em formato de dicionário.
        
        Returns:
            Dicionário {vencimento: {dados do título}}
        """
        dados = {}
        
        for vencimento, titulo in self._titulos.items():
            dados[vencimento] = {
                "pu_termo": titulo.pu_termo if titulo.pu_termo else None,
                "pu_d0": titulo.pu_d0 if titulo.pu_d0 else None,
                "quantidade": titulo.quantidade,
                "financeiro": titulo.financeiro if titulo.financeiro else None,
            }
        
        return dados
    
    @property
    def vencimentos(self) -> List[str]:
        """Lista de vencimentos disponíveis."""
        return sorted(list(self._titulos.keys()))
    
    @property
    def total_titulos(self) -> int:
        """Número total de títulos na carteira."""
        return len(self._titulos)




