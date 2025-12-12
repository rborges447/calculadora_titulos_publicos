"""
Utilitários para a API
"""
import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd

# Caminho para arquivo de controle de atualização
CONTROLE_ATUALIZACAO_FILE = Path("api/.ultima_atualizacao.json")


def precisa_atualizar_mercado() -> bool:
    """
    Verifica se as variáveis de mercado precisam ser atualizadas.
    Atualiza uma vez por dia.
    
    Returns:
        bool: True se precisa atualizar, False caso contrário
    """
    hoje = date.today().isoformat()
    
    # Se o arquivo não existe, precisa atualizar
    if not CONTROLE_ATUALIZACAO_FILE.exists():
        return True
    
    try:
        # Ler data da última atualização
        with open(CONTROLE_ATUALIZACAO_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            ultima_atualizacao = dados.get('data', '')
            
        # Se a última atualização foi hoje, não precisa atualizar
        if ultima_atualizacao == hoje:
            return False
        
        # Se foi em outro dia, precisa atualizar
        return True
    except Exception:
        # Se houver erro ao ler, assume que precisa atualizar
        return True


def marcar_atualizado():
    """
    Marca que as variáveis de mercado foram atualizadas hoje
    """
    try:
        # Criar diretório se não existir
        CONTROLE_ATUALIZACAO_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar data de hoje
        dados = {
            'data': date.today().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(CONTROLE_ATUALIZACAO_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2)
    except Exception as e:
        print(f"Erro ao marcar atualização: {e}")


def get_ultima_atualizacao() -> str:
    """
    Retorna a data da última atualização
    
    Returns:
        str: Data da última atualização ou "Nunca"
    """
    if not CONTROLE_ATUALIZACAO_FILE.exists():
        return "Nunca"
    
    try:
        with open(CONTROLE_ATUALIZACAO_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados.get('data', 'Nunca')
    except Exception:
        return "Nunca"


def serialize_datetime(dt) -> str:
    """
    Serializa datetime para string ISO (YYYY-MM-DD).
    
    Args:
        dt: Objeto datetime, pd.Timestamp ou None
    
    Returns:
        str: Data formatada ou None
    """
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        return dt.strftime("%Y-%m-%d")
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return str(dt)






