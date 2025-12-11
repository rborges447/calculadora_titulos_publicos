"""
Utilitários para interagir com a API de carteiras.
"""

import requests
from typing import Dict, Optional, List
from dash_app.config import API_URL


def criar_carteira(tipo: str, dias_liquidacao: int = 1, quantidade_padrao: Optional[float] = None) -> tuple[bool, Dict]:
    """
    Cria uma nova carteira.
    
    Args:
        tipo: Tipo do título ('ltn', 'lft', 'ntnb', 'ntnf')
        dias_liquidacao: Dias para liquidação
        quantidade_padrao: Quantidade padrão (opcional)
    
    Returns:
        (sucesso, dados) onde dados contém carteira_id e titulos
    """
    try:
        url = f"{API_URL}/carteiras/{tipo.lower()}"
        payload = {
            "dias_liquidacao": dias_liquidacao,
        }
        if quantidade_padrao:
            payload["quantidade_padrao"] = quantidade_padrao
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro ao criar carteira {tipo}: {e}")
        return False, {"error": str(e)}


def atualizar_taxa(tipo: str, carteira_id: str, vencimento: str, taxa: float) -> tuple[bool, Dict]:
    """
    Atualiza a taxa de um título específico na carteira.
    
    Args:
        tipo: Tipo do título ('ltn', 'ntnb', 'ntnf')
        carteira_id: ID da carteira (já contém o prefixo do tipo)
        vencimento: Data de vencimento (YYYY-MM-DD)
        taxa: Nova taxa
    
    Returns:
        (sucesso, dados atualizados)
    """
    try:
        url = f"{API_URL}/carteiras/{carteira_id}/taxa"
        payload = {
            "vencimento": vencimento,
            "taxa": float(taxa),
        }
        
        response = requests.put(url, json=payload, timeout=30)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro ao atualizar taxa: {e}")
        return False, {"error": str(e)}


def atualizar_premio_di(tipo: str, carteira_id: str, vencimento: str, premio: float, di: float) -> tuple[bool, Dict]:
    """
    Atualiza prêmio e DI de um título específico na carteira.
    
    Args:
        tipo: Tipo do título ('ltn', 'ntnf')
        carteira_id: ID da carteira (já contém o prefixo do tipo)
        vencimento: Data de vencimento (YYYY-MM-DD)
        premio: Prêmio sobre DI
        di: Taxa DI de referência
    
    Returns:
        (sucesso, dados atualizados)
    """
    try:
        url = f"{API_URL}/carteiras/{carteira_id}/premio-di"
        payload = {
            "vencimento": vencimento,
            "premio": float(premio),
            "di": float(di),
        }
        
        response = requests.put(url, json=payload, timeout=30)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro ao atualizar prêmio+DI: {e}")
        return False, {"error": str(e)}


def atualizar_dias_liquidacao(tipo: str, carteira_id: str, dias: int) -> tuple[bool, Dict]:
    """
    Atualiza dias de liquidação para todos os títulos da carteira.
    
    Args:
        tipo: Tipo do título
        carteira_id: ID da carteira (já contém o prefixo do tipo)
        dias: Novo número de dias
    
    Returns:
        (sucesso, dados atualizados)
    """
    try:
        url = f"{API_URL}/carteiras/{carteira_id}/dias"
        payload = {
            "dias": int(dias),
        }
        
        response = requests.put(url, json=payload, timeout=60)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro ao atualizar dias: {e}")
        return False, {"error": str(e)}


def obter_carteira(tipo: str, carteira_id: str) -> tuple[bool, Dict]:
    """
    Obtém os dados atuais da carteira.
    
    Args:
        tipo: Tipo do título
        carteira_id: ID da carteira (já contém o prefixo do tipo)
    
    Returns:
        (sucesso, dados da carteira)
    """
    try:
        url = f"{API_URL}/carteiras/{carteira_id}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro ao obter carteira: {e}")
        return False, {"error": str(e)}

