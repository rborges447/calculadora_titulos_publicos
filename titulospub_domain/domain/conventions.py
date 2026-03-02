"""
Convenções financeiras e constantes do domínio.
"""
from math import trunc

# Convenções de contagem de dias
DIAS_UTEIS_ANO = 252
DIAS_CALENDARIO_ANO = 365.25

# Função de truncamento padrão (usada em todo o módulo)
def truncar(valor: float, casas_decimais: int) -> float:
    """
    Trunca um valor para um número específico de casas decimais.
    
    Args:
        valor: Valor a truncar
        casas_decimais: Número de casas decimais
        
    Returns:
        Valor truncado
    """
    return trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais

# Precisões padrão
PRECISAO_PU = 6  # 6 casas decimais para PU
PRECISAO_COTACAO = 4  # 4 casas decimais para cotação
PRECISAO_TAXA = 4  # 4 casas decimais para taxa
PRECISAO_FATOR = 14  # 14 casas decimais para fatores intermediários
