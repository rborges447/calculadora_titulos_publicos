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
    app.run(debug=debug_mode, port=8050, host="127.0.0.1")


