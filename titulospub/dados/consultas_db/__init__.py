"""Consulta exploratória ao SQLite gold (bbdb), separada de ``VariaveisMercado``.

Spec: ``specs/003-consulta-db-explorer/003-consulta-db-explorer.md``

Toda a lógica de consulta (catálogo, leitura, CSV) fica neste pacote.
A API e o Dash apenas delegam via HTTP.
"""

from .catalogo import FonteConsulta, listar_catalogo, obter_fonte
from .disponibilidade import obter_intervalo_disponivel
from .excecoes import (
    BancoIndisponivelError,
    ColunasInvalidasError,
    ConsultaDbError,
    IntervaloSemDadosError,
    LimiteExportacaoError,
    TabelaAusenteNoBancoError,
    TabelaDesconhecidaError,
)
from .servico import (
    ConsultaResultado,
    consultar,
    exportar_csv,
)

__all__ = [
    "BancoIndisponivelError",
    "ColunasInvalidasError",
    "ConsultaDbError",
    "ConsultaResultado",
    "FonteConsulta",
    "IntervaloSemDadosError",
    "LimiteExportacaoError",
    "TabelaAusenteNoBancoError",
    "TabelaDesconhecidaError",
    "consultar",
    "exportar_csv",
    "listar_catalogo",
    "obter_fonte",
    "obter_intervalo_disponivel",
]
