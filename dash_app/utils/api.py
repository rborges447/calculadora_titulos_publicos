"""
Cliente HTTP simples para a API FastAPI.

Este módulo fornece funções para fazer requisições HTTP à API FastAPI.
Todas as funções retornam uma tupla (sucesso: bool, resultado_ou_erro).
"""

import os
import re

import requests

from dash_app import config

CONSULTAS_DB_TIMEOUT = int(os.getenv("CONSULTAS_DB_TIMEOUT", "120"))


def _http_error_detail(exc: requests.exceptions.HTTPError) -> str:
    """Extrai mensagem legível do corpo JSON da API (FastAPI ``detail``)."""
    response = exc.response
    if response is not None:
        try:
            body = response.json()
            detail = body.get("detail")
            if isinstance(detail, str):
                return detail
            if detail is not None:
                return str(detail)
        except (ValueError, AttributeError):
            pass
    return str(exc)


def _filename_from_content_disposition(header: str) -> str:
    if not header:
        return "consulta.csv"
    match = re.search(r'filename="?([^";\n]+)"?', header)
    if match:
        return match.group(1).strip()
    return "consulta.csv"


def _request_error(exc: requests.exceptions.RequestException) -> str:
    if isinstance(exc, requests.exceptions.HTTPError):
        return _http_error_detail(exc)
    return str(exc)


def post(endpoint: str, payload: dict, timeout: int = 15):
    """
    Envia requisição POST para a API FastAPI.

    Returns:
        tuple: (sucesso: bool, resultado_ou_erro)
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, _request_error(exc)


def get(endpoint: str, timeout: int = 15):
    """
    Envia requisição GET para a API FastAPI.

    Returns:
        tuple: (sucesso: bool, resultado_ou_erro)
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, _request_error(exc)


def put(endpoint: str, payload: dict, timeout: int = 15):
    """
    Envia requisição PUT para a API FastAPI.

    Returns:
        tuple: (sucesso: bool, resultado_ou_erro)
    """
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.put(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.RequestException as exc:
        return False, _request_error(exc)


def post_bytes(endpoint: str, payload: dict, timeout: int | None = None):
    """
    POST com resposta binária (ex.: exportação CSV).

    Returns:
        tuple: (True, (bytes, filename)) ou (False, mensagem_erro)
    """
    if timeout is None:
        timeout = CONSULTAS_DB_TIMEOUT
    url = f"{config.API_URL}{endpoint}"
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        filename = _filename_from_content_disposition(
            resp.headers.get("Content-Disposition", "")
        )
        return True, (resp.content, filename)
    except requests.exceptions.RequestException as exc:
        return False, _request_error(exc)
