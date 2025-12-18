"""
Utilitários para formatação de números no padrão brasileiro.
"""


def formatar_numero_brasileiro(valor: float, casas_decimais: int = 6) -> str:
    """
    Formata um número no padrão brasileiro (vírgula para decimal, ponto para milhar).
    
    Args:
        valor: Número a ser formatado
        casas_decimais: Número de casas decimais (padrão: 6)
    
    Returns:
        String formatada no padrão brasileiro (ex: "1.234,56")
    """
    if valor is None:
        return ""
    
    try:
        # Formatar com vírgula como separador de milhar (padrão Python)
        # Python formata como "1,234.56" (vírgula para milhar, ponto para decimal)
        valor_str = f"{valor:,.{casas_decimais}f}"
        # Precisamos inverter: "1.234,56" (ponto para milhar, vírgula para decimal)
        partes = valor_str.split(".")
        if len(partes) == 2:
            # Tem parte decimal
            parte_inteira = partes[0].replace(",", ".")  # Trocar vírgula por ponto (milhar)
            parte_decimal = partes[1]
            return f"{parte_inteira},{parte_decimal}"
        else:
            # Sem parte decimal - apenas trocar vírgula por ponto
            return valor_str.replace(",", ".")
    except (ValueError, TypeError):
        return str(valor) if valor else ""


def parse_numero_brasileiro(valor_str: str) -> float:
    """
    Converte uma string no formato brasileiro para float.
    
    Args:
        valor_str: String no formato brasileiro (ex: "1.234,56" ou "7,5")
    
    Returns:
        Float correspondente ou None se inválido
    """
    if not valor_str or valor_str == "":
        return None
    
    try:
        # Remover pontos (separadores de milhar) e substituir vírgula por ponto
        valor_limpo = valor_str.strip().replace(".", "").replace(",", ".")
        return float(valor_limpo)
    except (ValueError, TypeError):
        return None


def formatar_taxa_brasileira(valor: float) -> str:
    """Formata taxa com 4 casas decimais no padrão brasileiro"""
    return formatar_numero_brasileiro(valor, casas_decimais=4)


def formatar_pu_brasileiro(valor: float) -> str:
    """Formata PU com 6 casas decimais no padrão brasileiro"""
    return formatar_numero_brasileiro(valor, casas_decimais=6)


def formatar_bps(valor: float) -> str:
    """Formata pontos base com 2 casas decimais no padrão brasileiro"""
    return formatar_numero_brasileiro(valor, casas_decimais=2)


def formatar_dv01(valor: float) -> str:
    """Formata DV01 com 2 casas decimais no padrão brasileiro"""
    return formatar_numero_brasileiro(valor, casas_decimais=2)


def formatar_inteiro(valor: int) -> str:
    """Formata número inteiro no padrão brasileiro"""
    if valor is None:
        return ""
    return formatar_numero_brasileiro(float(valor), casas_decimais=0)
