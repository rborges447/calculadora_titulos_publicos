# =========================
# TITULOS_PUBLICOS
# =========================

TITULOS_PUBLICOS_COLUMNS = [
    "id",
    "expressao",
    "data_vencimento",
    "tipo_titulo",
    "data_base",
    "codigo_selic",
    "codigo_isin",
    "status",
]

TITULOS_PUBLICOS_REQUIRED = [
    "tipo_titulo",
    "data_vencimento",
]

TITULOS_PUBLICOS_UNIQUE = [
    "tipo_titulo",
    "data_vencimento",
]

# =========================
# MERCADO_SECUNDARIO
# =========================

MERCADO_SECUNDARIO_COLUMNS = [
    "titulo_id",
    "data_referencia",
    "taxa_anbima",
    "intervalo_min_d0",
    "intervalo_max_d0",
    "intervalo_min_d1",
    "intervalo_max_d1",
    "pu",
]

MERCADO_SECUNDARIO_REQUIRED = [
    "titulo_id",
    "data_referencia",
]

MERCADO_SECUNDARIO_NUMERIC = [
    "taxa_anbima",
    "intervalo_min_d0",
    "intervalo_max_d0",
    "intervalo_min_d1",
    "intervalo_max_d1",
    "pu",
]

# =========================
# RENAMES (API -> BANCO)
# =========================

MERCADO_SECUNDARIO_RENAME_MAP = {
    "taxa_indicativa": "taxa_anbima",
}
