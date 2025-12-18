"""
Configurações globais do app Dash.
"""

import os

# URL da API FastAPI - configurável via variável de ambiente
# Default: localhost para desenvolvimento local
# Para rede: export API_BASE_URL=http://10.182.129.1:8000
API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

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

