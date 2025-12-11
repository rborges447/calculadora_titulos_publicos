"""
Configurações globais do app Dash.
"""

# URL da API FastAPI
API_URL = "http://localhost:8000"

# Metadados do app
APP_TITLE = "Calculadora de Títulos Públicos"
APP_DESCRIPTION = "Interface web para cálculo de LTN, LFT, NTNB e NTNF"

# Rotas das páginas
PAGES = {
    "home": {"label": "Home", "path": "/"},
    "ltn": {"label": "LTN", "path": "/ltn"},
    "lft": {"label": "LFT", "path": "/lft"},
    "ntnb": {"label": "NTNB", "path": "/ntnb"},
    "ntnf": {"label": "NTNF", "path": "/ntnf"},
}

