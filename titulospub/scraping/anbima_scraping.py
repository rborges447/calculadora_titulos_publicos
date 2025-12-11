import pandas as pd
import requests
import re

def scrap_anbimas(data)-> pd.DataFrame: 
    """""
    Puxa as o DataFrame "cru" com as anbimas
    
    PARAMETROS: 
    
        data
    """""

    #Fazendo as conversões necessárias de dia, mes e ano
    dia = f"{data.day:02}" if data.day < 10 else str(data.day)
    mes = f"{data.month:02}" if data.month < 10 else str(data.month)
    ano = str(data.year)[2:]

    #Difinindo o caminho do arquivo
    caminho = f"https://www.anbima.com.br/informacoes/merc-sec/arqs/ms{ano}{mes}{dia}.txt"

    #Lendo o DataFrame
    anbima_df = pd.read_csv(caminho, sep='@', encoding='latin1', header=1)
    
    #Retornando o DataFrame com as Anbimas
    return anbima_df

def scrap_cdi():
    cdi_df = pd.read_excel("https://www.anbima.com.br/informacoes/indicadores/arqs/indicadores.xls")
    cdi_float = cdi_df[cdi_df.iloc[:, 0] == "Estimativa SELIC1"].iloc[0, 2]

    return cdi_float

def scrap_feriados():
    # Definindo o caminho para ler o DataFrame
    caminho = "https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls"

    # Fazendo a leitura do DataFrame com o pandas
    feriados_df = pd.read_excel(caminho)

    # Removendo os valores NaN do DataFrame
    feriados_df.dropna(inplace=True)

    # Transformando os valores para o formato data do pandas e convertendo numa lista
    feriados_lista = pd.to_datetime(feriados_df['Data']).to_list()

    # Retornando a Series com as datas
    return feriados_lista

def scrap_proj_ipca():

    proj_df = pd.read_excel("https://www.anbima.com.br/informacoes/indicadores/arqs/indicadores.xls")
    proj_float = proj_df[proj_df.iloc[:, 0] == "IPCA1"].iloc[0, 2]
    
    return proj_float

def scrap_vna_lft(data: pd.Timestamp):

    #trabalhando a data
    dia = f"{data.day:02}" if data.day < 10 else str(data.day)
    mes = f"{data.month:02}" if data.month < 10 else str(data.month)
    ano = str(data.year)

    # Baixar o arquivo .tex da internet
    response = requests.get(f"https://www.anbima.com.br/informacoes/res-238/arqs/{ano}{mes}{dia}_238.tex")

    if response.status_code != 200:
        raise Exception(f"Erro ao baixar o arquivo: {response.status_code}")

        # Supondo que o arquivo .tex tenha dados tabulares
    linhas = response.text.split("\n")  # Separar por linhas
    linhas = linhas[3]

    # String de exemplo
    texto = linhas

    # Expressão regular para encontrar o valor na última coluna (índice)
    padrao = r"\d{2}/\d{2}/\d{4}\s+(\d{1,3}(?:\.\d{3})*,\d+)"

    # Encontrar o valor do índice
    match = re.search(padrao, texto)

    # Se encontrou, pegar o valor
    if match:
        numero_str = match.group(1)
        # Remover o ponto (milhar) e substituir a vírgula por ponto
        numero_float = float(numero_str.replace('.', '').replace(',', '.'))
        return numero_float  # Deve exibir o valor como float
    else:
        raise ValueError(f"Não foi possível encontrar o VNA LFT na data {data.strftime('%Y-%m-%d')}")

# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
    print("anbima_clients")