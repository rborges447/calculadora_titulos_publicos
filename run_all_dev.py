"""
Script de conveniência para desenvolvimento local.

Sobe a API FastAPI e a aplicação Dash em paralelo, utilizando
os scripts existentes `run_api.py` e `run_dash_app.py`.

Uso:
    python run_all_dev.py

Este script NÃO é pensado para produção. Em ambiente produtivo,
use um servidor de aplicações adequado (uvicorn/gunicorn para a API,
servidor próprio para o Dash) e orquestração externa.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import List


def main() -> None:
    env = os.environ.copy()

    processes: List[subprocess.Popen] = []

    try:
        # Inicia API (run_api.py)
        api_proc = subprocess.Popen(
            [sys.executable, "run_api.py"],
            env=env,
        )
        processes.append(api_proc)

        # Inicia Dash (run_dash_app.py)
        dash_proc = subprocess.Popen(
            [sys.executable, "run_dash_app.py"],
            env=env,
        )
        processes.append(dash_proc)

        print("API e Dash iniciados. Pressione Ctrl+C para encerrar ambos.")

        # Espera até que um dos processos termine ou até Ctrl+C
        while True:
            still_running = [p for p in processes if p.poll() is None]
            if not still_running:
                break
    except KeyboardInterrupt:
        print("\nEncerrando processos (API e Dash)...")
    finally:
        for proc in processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass

        for proc in processes:
            try:
                proc.wait(timeout=10)
            except Exception:
                pass

        print("Todos os processos filhos foram encerrados.")


if __name__ == "__main__":
    main()

