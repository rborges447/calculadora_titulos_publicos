"""
Função para cálculo de equivalência entre títulos públicos
"""
from .lft.titulo_lft import LFT
from .ltn.titulo_ltn import LTN
from .ntnb.titulo_ntnb import NTNB
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

    # Validação: LFT não suporta equivalência por DV01
    if criterio == "dv":
        if titulo1 == "LFT" or titulo2 == "LFT":
            raise ValueError("LFT não suporta equivalência por DV01. Use critério 'fin' (financeiro) para LFT.")

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
        # Validação adicional após instanciação (caso algum título tenha sido criado incorretamente)
        if isinstance(titulo_1, LFT) or isinstance(titulo_2, LFT):
            raise ValueError("LFT não suporta equivalência por DV01. Use critério 'fin' (financeiro) para LFT.")
        if titulo_1.dv01 is None or titulo_2.dv01 is None:
            raise ValueError("DV01 não disponível para um dos títulos")
        eq = titulo_1.dv01 / titulo_2.dv01 * qtd1
    elif criterio == "fin":
        # Calcula financeiro do primeiro título (já tem quantidade definida)
        financeiro_1 = titulo_1.financeiro
        
        # Calcula quantidade equivalente do segundo título
        # Para isso, precisamos calcular quanto do título 2 equivale ao financeiro do título 1
        # financeiro_1 = quantidade_2 * pu_termo_2
        # quantidade_2 = financeiro_1 / pu_termo_2
        titulo_2.quantidade = 1  # Quantidade unitária para obter PU
        pu_termo_2 = titulo_2.pu_termo if hasattr(titulo_2, 'pu_termo') else titulo_2.pu_d0
        eq = financeiro_1 / pu_termo_2
    else:
        raise ValueError(f"Critério '{criterio}' não reconhecido. Use 'dv' ou 'fin'")

    return eq