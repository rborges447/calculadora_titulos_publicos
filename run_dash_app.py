"""
Script para executar a aplicação Dash
"""
from dash_app.app import app

if __name__ == "__main__":
    # Dash >=2.16 substituiu run_server por run
    app.run(debug=True, port=8050, host="127.0.0.1")


