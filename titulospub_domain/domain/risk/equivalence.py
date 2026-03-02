"""
Cálculo de equivalência entre títulos públicos.
"""
from typing import Optional
from ..instruments import LTN, LFT, NTNB, NTNF


def equivalencia(
    titulo1: str,
    venc1: str,
    titulo2: str,
    venc2: str,
    qtd1: Optional[int] = None,
    tx1: Optional[float] = None,
    tx2: Optional[float] = None,
    criterio: Optional[str] = None,
    feriados: Optional[list] = None,
    market_data_provider=None
):
    """
    Calcula a equivalência entre dois títulos públicos.
    
    Args:
        titulo1: Tipo do primeiro título ("NTNB", "LTN", "LFT", "NTNF")
        venc1: Data de vencimento do primeiro título
        titulo2: Tipo do segundo título
        venc2: Data de vencimento do segundo título
        qtd1: Quantidade do primeiro título (obrigatório)
        tx1: Taxa do primeiro título (opcional)
        tx2: Taxa do segundo título (opcional)
        criterio: Critério de equivalência ("dv" ou "fin")
        feriados: Lista de feriados (obrigatório)
        market_data_provider: Provedor de dados de mercado (opcional)
    
    Returns:
        Equivalência calculada
    """
    # Mapeamento dos tipos de título
    mapa_titulos = {
        "NTNB": NTNB,
        "LTN": LTN,
        "LFT": LFT,
        "NTNF": NTNF
    }

    if titulo1 not in mapa_titulos:
        raise KeyError(f"Tipo de título '{titulo1}' não reconhecido.")
    if titulo2 not in mapa_titulos:
        raise KeyError(f"Tipo de título '{titulo2}' não reconhecido.")

    if criterio == "dv":
        if titulo1 == "LFT" or titulo2 == "LFT":
            raise ValueError("LFT não suporta equivalência por DV01.")

    # Instancia as classes
    kwargs = {}
    if feriados:
        kwargs['feriados'] = feriados
    if market_data_provider:
        kwargs['market_data_provider'] = market_data_provider
    
    titulo_1 = mapa_titulos[titulo1](data_vencimento_titulo=venc1, **kwargs)
    titulo_2 = mapa_titulos[titulo2](data_vencimento_titulo=venc2, **kwargs)

    # Define taxas se fornecidas
    if tx1 is not None:
        titulo_1.taxa = tx1
    if tx2 is not None:
        titulo_2.taxa = tx2
    
    # Define quantidade
    if qtd1 is not None:
        titulo_1.quantidade = qtd1
    else:
        raise ValueError("Parâmetro 'qtd1' é obrigatório")
    
    # Calcula equivalência
    if criterio == "dv":
        if titulo_1.dv01 is None or titulo_2.dv01 is None:
            raise ValueError("DV01 não disponível para um dos títulos")
        eq = titulo_1.dv01 / titulo_2.dv01 * qtd1
    elif criterio == "fin":
        financeiro_1 = titulo_1.financeiro
        titulo_2.quantidade = 1
        pu_termo_2 = titulo_2.pu_termo if hasattr(titulo_2, 'pu_termo') else titulo_2.pu_d0
        eq = financeiro_1 / pu_termo_2
    else:
        raise ValueError(f"Critério '{criterio}' não reconhecido. Use 'dv' ou 'fin'")

    return eq
