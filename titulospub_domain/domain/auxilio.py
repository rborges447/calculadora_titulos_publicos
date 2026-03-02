"""
Funções auxiliares compartilhadas.
"""
import pandas as pd


def codigo_vencimento_bmf(codigo: str) -> pd.Timestamp:
    """
    Converte código BMF em data de vencimento.
    
    Args:
        codigo: Código BMF (ex: "DI1F27")
        
    Returns:
        Data de vencimento
    """
    letras = {
        "F": "01", "G": "02", "H": "03",
        "J": "04", "K": "05", "M": "06",
        "N": "07", "Q": "08", "U": "09",
        "V": "10", "X": "11", "Z": "12"
    }

    for k, v in letras.items():
        codigo = codigo.replace(k, v)

    dia = "01"
    mes = codigo[3:5]
    ano = str(int(codigo[5:]) + 2000)

    data_vencimento = f"{ano}-{mes}-{dia}"
    return pd.to_datetime(data_vencimento)


def vencimento_codigo_bmf(data_vencimento: pd.Timestamp, prefixo: str) -> str:
    """
    Converte data de vencimento em código BMF.
    
    Args:
        data_vencimento: Data de vencimento
        prefixo: Prefixo do código (ex: "DI1", "DAP")
        
    Returns:
        Código BMF
    """
    letras = {
        "01": "F", "02": "G", "03": "H",
        "04": "J", "05": "K", "06": "M",
        "07": "N", "08": "Q", "09": "U",
        "10": "V", "11": "X", "12": "Z"
    }

    dt = data_vencimento.strftime("%Y-%m-%d")
    ano = dt[2:4]
    mes = dt[5:7]

    for k, v in letras.items():
        mes = mes.replace(k, v)

    codigo = f"{prefixo}{mes}{ano}"
    return codigo
