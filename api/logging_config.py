"""
Configuração de logging estruturado para a API.

Este módulo fornece logging estruturado sem remover prints existentes,
permitindo migração gradual e melhor observabilidade em produção.
"""
import logging
import sys
from pathlib import Path

# Configurar logger raiz da API
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

# Evitar duplicação de handlers
if not logger.handlers:
    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato simples e legível
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.propagate = False


def get_logger(name: str = "api") -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome do logger (padrão: "api")
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
