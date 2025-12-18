"""
Script para executar a aplicação Dash.

Para desenvolvimento: DEBUG=True python run_dash_app.py
Para produção: python run_dash_app.py (debug=False por padrão)
"""
import os

from dash_app.app import app

if __name__ == "__main__":
    # Dash >=2.16 substituiu run_server por run
    # Usar variável de ambiente para controlar debug (padrão: False para produção)
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    # Usar 0.0.0.0 para permitir acesso pela rede interna
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))
    app.run(debug=debug_mode, port=port, host=host)


