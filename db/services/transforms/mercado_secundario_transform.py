import pandas as pd

def transform_mercado_secundario_df(df: pd.DataFrame) -> pd.DataFrame:

    if df is None or df.empty:
        return df
    
    df = df.copy()

    if "taxa_indicativa" in df.columns and "taxa_anbima" not in df.columns:
        df = df.rename(columns={"taxa_indicativa": "taxa_anbima"})
    
    return df
