"""
Funções utilitárias para buscar vencimentos e códigos disponíveis via API.
"""
import requests
from typing import List, Optional
from dash_app.config import API_URL


def get_vencimentos_ltn() -> List[str]:
    """
    Busca lista de vencimentos disponíveis para LTN.
    
    Returns:
        List[str]: Lista de datas no formato YYYY-MM-DD
    """
    try:
        response = requests.get(f"{API_URL}/vencimentos/ltn", timeout=30)
        response.raise_for_status()
        result = response.json()
        print(f"[API] Vencimentos LTN recebidos: {len(result)} itens")
        return result
    except requests.exceptions.ConnectionError:
        print(f"[ERRO] Nao foi possivel conectar a API em {API_URL}")
        return []
    except Exception as e:
        print(f"[ERRO] Erro ao buscar vencimentos LTN: {e}")
        return []


def get_vencimentos_lft() -> List[str]:
    """
    Busca lista de vencimentos disponíveis para LFT.
    
    Returns:
        List[str]: Lista de datas no formato YYYY-MM-DD
    """
    try:
        response = requests.get(f"{API_URL}/vencimentos/lft", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar vencimentos LFT: {e}")
        return []


def get_vencimentos_ntnb() -> List[str]:
    """
    Busca lista de vencimentos disponíveis para NTNB.
    
    Returns:
        List[str]: Lista de datas no formato YYYY-MM-DD
    """
    try:
        response = requests.get(f"{API_URL}/vencimentos/ntnb", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar vencimentos NTNB: {e}")
        return []


def get_vencimentos_ntnf() -> List[str]:
    """
    Busca lista de vencimentos disponíveis para NTNF.
    
    Returns:
        List[str]: Lista de datas no formato YYYY-MM-DD
    """
    try:
        response = requests.get(f"{API_URL}/vencimentos/ntnf", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar vencimentos NTNF: {e}")
        return []


def get_codigos_di() -> List[str]:
    """
    Busca lista de códigos DI disponíveis.
    
    Returns:
        List[str]: Lista de códigos DI (ex: DI1F32, DI1F33, etc)
    """
    try:
        response = requests.get(f"{API_URL}/vencimentos/di", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar códigos DI: {e}")
        return []


def formatar_data_para_exibicao(data: str) -> str:
    """
    Formata data de YYYY-MM-DD para DD/MM/YYYY para exibição.
    
    Args:
        data: Data no formato YYYY-MM-DD
        
    Returns:
        str: Data formatada como DD/MM/YYYY
    """
    try:
        partes = data.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return data
    except:
        return data

