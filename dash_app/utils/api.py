"""
Cliente HTTP simples para a API FastAPI.

Este módulo fornece funções para fazer requisições HTTP à API FastAPI.
Todas as funções retornam uma tupla (sucesso: bool, resultado_ou_erro).
"""

import requests

from dash_app import config


def post(endpoint: str, payload: dict, timeout: int = 15):
    """
    Envia requisição POST para a API FastAPI.
    
    Args:
        endpoint: Endpoint da API (ex: "/titulos/ltn")
        payload: Dados a enviar no corpo da requisição (será convertido para JSON)
        timeout: Timeout da requisição em segundos (padrão: 15)
    
    Returns:
        tuple: (sucesso: bool, resultado_ou_erro)
            - Se sucesso=True: resultado_ou_erro contém o JSON da resposta
            - Se sucesso=False: resultado_ou_erro contém mensagem de erro
    
    Exemplo:
        sucesso, resultado = post("/titulos/ltn", {"data_vencimento": "2025-01-01"})
        if sucesso:
            print(resultado["pu_d0"])
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
    Envia requisição GET para a API FastAPI.
    
    Args:
        endpoint: Endpoint da API (ex: "/vencimentos/ltn")
        timeout: Timeout da requisição em segundos (padrão: 15)
    
    Returns:
        tuple: (sucesso: bool, resultado_ou_erro)
            - Se sucesso=True: resultado_ou_erro contém o JSON da resposta
            - Se sucesso=False: resultado_ou_erro contém mensagem de erro
    
    Exemplo:
        sucesso, resultado = get("/vencimentos/ltn")
        if sucesso:
            print(resultado["vencimentos"])
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, str(exc)


def put(endpoint: str, payload: dict, timeout: int = 15):
    """
    Envia requisição PUT para a API FastAPI.
    
    Args:
        endpoint: Endpoint da API (ex: "/carteiras/{id}/taxa")
        payload: Dados a enviar no corpo da requisição (será convertido para JSON)
        timeout: Timeout da requisição em segundos (padrão: 15)
    
    Returns:
        tuple: (sucesso: bool, resultado_ou_erro)
            - Se sucesso=True: resultado_ou_erro contém o JSON da resposta
            - Se sucesso=False: resultado_ou_erro contém mensagem de erro
    
    Exemplo:
        sucesso, resultado = put("/carteiras/abc123/taxa", {"vencimento": "2025-01-01", "taxa": 13.0})
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.put(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, str(exc)
