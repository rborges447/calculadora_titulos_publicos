#from titulospub.scraping.anbima_scraping import scrap_anbimas
import pandas as pd

def anbimas(anbima_df):
    """"
    Retorna um dataframe para cada titulo com as apenas com as colunas que importam
    """ 
    #Deixando o df apenas com as colunas necessarias
    colunas = ["Titulo", "Data Referencia", "Data Vencimento", "Tx. Indicativas", "PU"]
    anbima_tratado_df = anbima_df[colunas].copy()

    #Transformando as colunas de data para o formato de data do pandas
    anbima_tratado_df["Data Referencia"] = pd.to_datetime(anbima_tratado_df["Data Referencia"], format="%Y%m%d")
    anbima_tratado_df["Data Vencimento"] = pd.to_datetime(anbima_tratado_df["Data Vencimento"], format="%Y%m%d")

    #Renomeando as colunas
    anbima_tratado_df.rename(columns={"Titulo":"TITULO","Data Referencia":"DATA" ,
                                      "Data Vencimento": "VENCIMENTO","Tx. Indicativas":"ANBIMA"}, inplace=True)

    #convertendo as colunas de data para float
    anbima_tratado_df["ANBIMA"] = (
        anbima_tratado_df["ANBIMA"]
        .astype(str)  # Garante que são strings
        .str.replace(r"\.", "", regex=True)  # Remove separadores de milhar
        .str.replace(r",", ".", regex=True)  # Troca vírgula decimal por ponto
    ).astype(float)

    #convertendo as colunas de data para float
    anbima_tratado_df["PU"] = (
        anbima_tratado_df["PU"]
        .astype(str)  # Garante que são strings
        .str.replace(r"\.", "", regex=True)  # Remove separadores de milhar
        .str.replace(r",", ".", regex=True)  # Troca vírgula decimal por ponto
    ).astype(float)

    #Criando um dicionario para os dataframes referentes a cada titulo
    dfs_dict = {}

    for titulo in anbima_tratado_df["TITULO"].unique():
        dfs_dict[titulo] = (anbima_tratado_df[anbima_tratado_df["TITULO"] == titulo]).reset_index()
        dfs_dict[titulo].drop(columns="index", inplace=True)

    return dfs_dict


if __name__ == "__main__":
    print("🔄 Testando processamento ANBIMA...")
    
    try:
        from titulospub.dados.backup import backup_anbimas
        
        print("📊 Carregando dados ANBIMA de backup...")
        anbimas_data = backup_anbimas()
        print(f"✅ Dados carregados: {len(anbimas_data)} tipos de títulos")
        
        print("📊 Processando dados ANBIMA...")
        processed = anbimas(anbimas_data)
        print(f"✅ Dados processados: {len(processed)} tipos de títulos")
        
        for titulo, df in processed.items():
            print(f"  - {titulo}: {len(df)} registros")
            if len(df) > 0:
                print(f"    Colunas: {list(df.columns)}")
                print(f"    Primeiro registro: {df.iloc[0].to_dict()}")
        
        print("✅ Processamento ANBIMA funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()