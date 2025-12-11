from nt import replace
import pandas as pd
import sidrapy

def puxar_valores_ipca_fechado():
      
    ipca_df = sidrapy.get_table(
        table_code="6691",  # Código da tabela IPCA com número-índice
        territorial_level="1",  # Brasil
        ibge_territorial_code="1",  # Código Brasil
        period="last 2"  # Últimos 2 meses
    )

    # Define a segunda linha como o cabeçalho
    ipca_df.columns = ipca_df.iloc[0]  # A segunda linha será usada como os novos cabeçalhos

    # Remove as duas primeiras linhas (pois a segunda linha foi usada como cabeçalho)
    ipca_df = ipca_df.drop([0, 0]).reset_index(drop=True)

    #Selecionando apenas os valores de numero indice e %
    ipca_df = ipca_df[(ipca_df["Variável (Código)"] == "2266") | (ipca_df["Variável (Código)"] == "63")]

    #Selecionando apenas as colunas necessárias
    ipca_df = ipca_df[["Mês", "Mês (Código)", "Unidade de Medida",  "Valor"]]

    #Renomeando as colunas
    ipca_df.rename(columns={"Mês": "DATA", "Mês (Código)": "DATA_CODIGO", 
                             "Unidade de Medida": "MEDIDA", "Valor": "VALOR"}, inplace=True)

    #Transformando a coluna de VALOR em float
    ipca_df["VALOR"] = ipca_df["VALOR"].astype(float)

    #Retornando o dataframe
    return ipca_df.reset_index(drop=True)

# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
    print("uptodata_clients")