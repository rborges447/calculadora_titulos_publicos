import pandas as pd 

def api_list_to_df(dados: list) -> pd.DataFrame:
    """
    Converte uma lista de dicionários em um DataFrame.
    """
    registros = [
        item
        for lista_do_dia in dados
        for item in (lista_do_dia or [])
        if isinstance (item, dict)
    ]

    if not registros:
        return pd.DataFrame()
    
    df = pd.DataFrame.from_records(registros)
    
    return df