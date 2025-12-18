"""
Cliente HTTP simples para a API FastAPI.
"""

import requests
from dash_app import config


def post(endpoint: str, payload: dict, timeout: int = 15):
    """
    Envia POST e retorna (sucesso, resultado_ou_erro).
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, str(exc)


def get(endpoint: str, timeout: int = 15):
    """
    Envia GET e retorna (sucesso, resultado_ou_erro).
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, str(exc)
