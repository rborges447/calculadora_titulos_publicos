"""
Função para cálculo de equivalência entre títulos públicos
"""
from .ntnb.titulo_ntnb import NTNB
from .ltn.titulo_ltn import LTN
from .lft.titulo_lft import LFT
from .ntnf.titulo_ntnf import NTNF


def equivalencia(titulo1: str, venc1: str, 
                 titulo2: str, venc2: str,
                 qtd1: int = None,
                 tx1: float = None, 
                 tx2: float = None,
                 criterio: str = None):
    """
    Calcula a equivalência entre dois títulos públicos.
    
    Args:
        titulo1: Tipo do primeiro título ("NTNB", "LTN", "LFT", "NTNF")
        venc1: Data de vencimento do primeiro título (formato: YYYY-MM-DD)
        titulo2: Tipo do segundo título ("NTNB", "LTN", "LFT", "NTNF")
        venc2: Data de vencimento do segundo título (formato: YYYY-MM-DD)
        qtd1: Quantidade do primeiro título (obrigatório)
        tx1: Taxa do primeiro título (opcional)
        tx2: Taxa do segundo título (opcional)
        criterio: Critério de equivalência ("dv" para DV01 ou "fin" para financeiro)
    
    Returns:
        float: Equivalência calculada
    
    Raises:
        KeyError: Se o tipo de título não for reconhecido
        ValueError: Se os parâmetros obrigatórios não forem fornecidos
    """
    # Mapeamento dos tipos de título para suas respectivas classes
    mapa_titulos = {
        "NTNB": NTNB,
        "LTN": LTN,
        "LFT": LFT,
        "NTNF": NTNF
    }

    # Verifica se o título está no dicionário
    if titulo1 not in mapa_titulos:
        raise KeyError(f"Tipo de título '{titulo1}' não reconhecido. Tipos disponíveis: {list(mapa_titulos.keys())}")
    if titulo2 not in mapa_titulos:
        raise KeyError(f"Tipo de título '{titulo2}' não reconhecido. Tipos disponíveis: {list(mapa_titulos.keys())}")

    # Instancia as classes correspondentes
    titulo_1 = mapa_titulos[titulo1](data_vencimento_titulo=venc1)
    titulo_2 = mapa_titulos[titulo2](data_vencimento_titulo=venc2)

    # Define taxas se fornecidas
    if tx1 is not None:
        titulo_1.taxa = tx1
    if tx2 is not None:
        titulo_2.taxa = tx2
    
    # Define quantidade do primeiro título
    if qtd1 is not None:
        titulo_1.quantidade = qtd1
    else:
        raise ValueError("Parâmetro 'qtd1' é obrigatório")

    # Calcula equivalência baseada no critério
    if criterio == "dv":
        if titulo_1.dv01 is None or titulo_2.dv01 is None:
            raise ValueError("DV01 não disponível para um dos títulos")
        eq = titulo_1.dv01 / titulo_2.dv01 * qtd1
    elif criterio == "fin":
        eq = titulo_1.financeiro / titulo_2.financeiro * qtd1
    else:
        raise ValueError(f"Critério '{criterio}' não reconhecido. Use 'dv' ou 'fin'")

    return eq