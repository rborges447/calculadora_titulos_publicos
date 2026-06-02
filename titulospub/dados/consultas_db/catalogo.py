"""Máscara estática (whitelist) de fontes consultáveis no gold bbdb."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .excecoes import TabelaDesconhecidaError

ModoConsulta = Literal["range", "snapshot"]

# --- Colunas alinhadas ao schema gold v2 (bbdb app/database/schema.py) ---

CDI_COLUMNS: tuple[str, ...] = ("data_referencia", "cdi")
PTAX_COLUMNS: tuple[str, ...] = ("data_referencia", "ptax_compra", "ptax_venda")
VNA_COLUMNS: tuple[str, ...] = (
    "data_referencia",
    "codigo_selic",
    "tipo_correcao",
    "index",
    "data_validade",
    "vna",
    "vna_ajustado",
)

# Manter em sync com bbdb: app/lake/gold/materializers/ipca_dict.py IPCA_DICT_COLUMNS
IPCA_DICT_COLUMNS: tuple[str, ...] = (
    "data_referencia",
    "ultimo_mes_ipca",
    "ref_month_atual",
    "ref_month_anterior",
    "indice_ipca_data_base",
    "indice_ipca_fechado_atual",
    "indice_ipca_fechado_anterior",
    "var_ipca_atual",
    "var_ipca_ant",
    "ipca_proj",
    "ipca_usado",
    "usa_fechado",
    "data_coleta_referencia",
    "ipca_proj_data_coleta",
    "inicio_mes_ipca",
    "fim_mes_ipca",
)

# Colunas do reader SQL (join CONTRATOS_BMF), não só AJUSTES_BMF_COLUMNS do schema INSERT
AJUSTES_BMF_COLUMNS: tuple[str, ...] = (
    "ticker",
    "data_referencia",
    "data_vencimento",
    "taxa_ajuste",
    "quantidade_ajuste",
)

MERCADO_SECUNDARIO_COLUMNS: tuple[str, ...] = (
    "tipo_titulo",
    "data_vencimento",
    "data_referencia",
    "taxa_anbima",
    "intervalo_min_d0",
    "intervalo_max_d0",
    "intervalo_min_d1",
    "intervalo_max_d1",
    "pu",
    "expressao",
    "data_base",
    "codigo_selic",
    "codigo_isin",
    "taxa_compra",
    "taxa_venda",
    "desvio_padrao",
    "status",
)

LIQUIDACOES_MERCADO_COLUMNS: tuple[str, ...] = (
    "tipo_titulo",
    "data_vencimento",
    "data_referencia",
    "qtd_operacoes",
    "qtd_titulos",
    "pu_medio",
    "expressao",
    "data_base",
    "codigo_selic",
    "codigo_isin",
    "status",
)

# Full outer SQL (mercado_liquidacoes_full_outer_*.sql) — aliases _mercado / _liq
MERCADO_COM_LIQUIDACOES_COLUMNS: tuple[str, ...] = (
    "tipo_titulo",
    "data_vencimento",
    "data_referencia",
    "taxa_anbima",
    "intervalo_min_d0",
    "intervalo_max_d0",
    "intervalo_min_d1",
    "intervalo_max_d1",
    "pu",
    "expressao_mercado",
    "data_base_mercado",
    "codigo_selic_mercado",
    "codigo_isin_mercado",
    "taxa_compra",
    "taxa_venda",
    "desvio_padrao",
    "status_mercado",
    "qtd_operacoes",
    "qtd_titulos",
    "pu_medio_liq",
    "expressao_liq",
    "data_base_liq",
    "codigo_selic_liq",
    "codigo_isin_liq",
    "status_liq",
)

LEILOES_COLUMNS: tuple[str, ...] = (
    "numero_edital",
    "tipo_titulo",
    "data_vencimento",
    "data_referencia",
    "oferta",
    "quantidade_aceita",
    "percentual_corte",
    "oferta_segunda_volta",
    "financeiro_aceito",
    "financeiro_aceito_segunda_volta",
    "quantidade_aceita_segunda_volta",
    "pu_medio",
    "taxa_media",
)

FERIADOS_COLUMNS: tuple[str, ...] = ("data",)

TITULOS_PUBLICOS_COLUMNS: tuple[str, ...] = (
    "tipo_titulo",
    "data_vencimento",
    "expressao",
    "data_base",
    "codigo_selic",
    "codigo_isin",
    "status",
)

CONTRATOS_BMF_COLUMNS: tuple[str, ...] = ("ticker", "codigo_isin", "data_vencimento")

GOLD_READER_ATTRS: frozenset[str] = frozenset(
    {
        "cdi",
        "ptax",
        "ipca_dict",
        "vna",
        "ajustes_bmf",
        "mercado_secundario",
        "liquidacoes_mercado",
        "mercado_com_liquidacoes",
        "leiloes",
        "feriados",
        "titulos_publicos",
        "contratos_bmf",
    }
)


@dataclass(frozen=True, slots=True)
class FonteConsulta:
    """Metadados de uma fonte gold consultável."""

    id: str
    rotulo: str
    reader_attr: str
    modo: ModoConsulta
    coluna_data: str | None
    colunas: tuple[str, ...]
    colunas_padrao: tuple[str, ...]
    descricao: str = ""


def _fonte(
    id: str,
    rotulo: str,
    modo: ModoConsulta,
    coluna_data: str | None,
    colunas: tuple[str, ...],
    colunas_padrao: tuple[str, ...],
    *,
    descricao: str = "",
    reader_attr: str | None = None,
) -> FonteConsulta:
    attr = reader_attr if reader_attr is not None else id
    return FonteConsulta(
        id=id,
        rotulo=rotulo,
        reader_attr=attr,
        modo=modo,
        coluna_data=coluna_data,
        colunas=colunas,
        colunas_padrao=colunas_padrao,
        descricao=descricao,
    )


_FONTES: tuple[FonteConsulta, ...] = (
    _fonte(
        "cdi",
        "CDI",
        "range",
        "data_referencia",
        CDI_COLUMNS,
        ("data_referencia", "cdi"),
    ),
    _fonte(
        "ptax",
        "PTAX",
        "range",
        "data_referencia",
        PTAX_COLUMNS,
        ("data_referencia", "ptax_compra", "ptax_venda"),
    ),
    _fonte(
        "ipca_dict",
        "IPCA (dict)",
        "range",
        "data_referencia",
        IPCA_DICT_COLUMNS,
        ("data_referencia", "ultimo_mes_ipca", "ipca_usado", "var_ipca_atual"),
        descricao="Série diária do dicionário IPCA materializado no gold.",
    ),
    _fonte(
        "vna",
        "VNA",
        "range",
        "data_referencia",
        VNA_COLUMNS,
        ("data_referencia", "codigo_selic", "vna", "vna_ajustado"),
    ),
    _fonte(
        "ajustes_bmf",
        "Ajustes BMF",
        "range",
        "data_referencia",
        AJUSTES_BMF_COLUMNS,
        ("ticker", "data_referencia", "data_vencimento", "taxa_ajuste"),
    ),
    _fonte(
        "mercado_secundario",
        "Mercado secundário",
        "range",
        "data_referencia",
        MERCADO_SECUNDARIO_COLUMNS,
        ("tipo_titulo", "data_vencimento", "data_referencia", "taxa_anbima", "pu"),
        descricao="Alto volume — prefira intervalos curtos.",
    ),
    _fonte(
        "liquidacoes_mercado",
        "Liquidações mercado",
        "range",
        "data_referencia",
        LIQUIDACOES_MERCADO_COLUMNS,
        ("tipo_titulo", "data_vencimento", "data_referencia", "qtd_operacoes", "pu_medio"),
        descricao="Alto volume — prefira intervalos curtos.",
    ),
    _fonte(
        "mercado_com_liquidacoes",
        "Mercado + liquidações",
        "range",
        "data_referencia",
        MERCADO_COM_LIQUIDACOES_COLUMNS,
        (
            "tipo_titulo",
            "data_vencimento",
            "data_referencia",
            "taxa_anbima",
            "pu",
            "qtd_operacoes",
            "pu_medio_liq",
        ),
        descricao="Full outer mercado/liquidações (colunas com sufixos _mercado/_liq).",
    ),
    _fonte(
        "leiloes",
        "Leilões",
        "range",
        "data_referencia",
        LEILOES_COLUMNS,
        ("data_referencia", "tipo_titulo", "data_vencimento", "taxa_media", "pu_medio"),
    ),
    _fonte(
        "feriados",
        "Feriados",
        "snapshot",
        "data",
        FERIADOS_COLUMNS,
        ("data",),
        descricao="Snapshot completo; filtro opcional por intervalo em memória.",
    ),
    _fonte(
        "titulos_publicos",
        "Títulos públicos",
        "snapshot",
        None,
        TITULOS_PUBLICOS_COLUMNS,
        ("tipo_titulo", "data_vencimento", "codigo_selic", "status"),
    ),
    _fonte(
        "contratos_bmf",
        "Contratos BMF",
        "snapshot",
        None,
        CONTRATOS_BMF_COLUMNS,
        ("ticker", "codigo_isin", "data_vencimento"),
    ),
)

_FONTES_POR_ID: dict[str, FonteConsulta] = {f.id: f for f in _FONTES}


def obter_fonte(tabela: str) -> FonteConsulta:
    """Resolve ``tabela`` no catálogo ou levanta ``TabelaDesconhecidaError``."""
    fonte = _FONTES_POR_ID.get(tabela)
    if fonte is None:
        raise TabelaDesconhecidaError(tabela)
    return fonte


def iter_fontes() -> tuple[FonteConsulta, ...]:
    """Todas as fontes registradas (ordem estável)."""
    return _FONTES


def listar_catalogo() -> list[dict]:
    """Metadados serializáveis para API/UI."""
    from .disponibilidade import obter_intervalo_disponivel
    from .excecoes import BancoIndisponivelError, TabelaAusenteNoBancoError

    fontes: list[dict] = []
    for f in _FONTES:
        item = {
            "id": f.id,
            "rotulo": f.rotulo,
            "reader_attr": f.reader_attr,
            "modo": f.modo,
            "coluna_data": f.coluna_data,
            "colunas": list(f.colunas),
            "colunas_padrao": list(f.colunas_padrao),
            "descricao": f.descricao,
            "data_disponivel_inicio": None,
            "data_disponivel_fim": None,
        }
        try:
            disp_min, disp_max = obter_intervalo_disponivel(f)
            if disp_min is not None:
                item["data_disponivel_inicio"] = disp_min.isoformat()
            if disp_max is not None:
                item["data_disponivel_fim"] = disp_max.isoformat()
        except (BancoIndisponivelError, TabelaAusenteNoBancoError, ValueError):
            # Banco ausente ou tabela ainda não materializada no SQLite local.
            pass
        fontes.append(item)
    return fontes
