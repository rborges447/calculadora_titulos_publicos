import os
import pandas as pd

def definir_caminho_adj_bmf(data):

    try:
        # Convertendo para string formatada
        dia = f"{data.day:02}"
        mes = f"{data.month:02}"
        ano = str(data.year)

        # Pasta
        pasta = f'x:\\Interest_Rate\\SettlementPrice\\{ano}{mes}{dia}\\'

        # Prefixo fixo do arquivo
        prefixo = f'Interest_Rate_SettlementPriceFile_Futures_{ano}{mes}{dia}_'

        # Verifica se a pasta existe
        if not os.path.exists(pasta):
            print(f"[AVISO] Pasta não encontrada: {pasta}")
            return None

        # Lista todos arquivos
        arquivos = os.listdir(pasta)

        # Filtra os que começam com prefixo e terminam com .csv
        arquivos_filtrados = [
            f for f in arquivos
            if f.startswith(prefixo) and f.endswith(".csv")
        ]

        if not arquivos_filtrados:
            print(f"[AVISO] Nenhum arquivo encontrado com prefixo {prefixo} na pasta {pasta}")
            return None

        # Extrai números finais
        numeros = []
        for arq in arquivos_filtrados:
            try:
                num_str = arq.replace(prefixo, "").replace(".csv", "")
                num = int(num_str)
                numeros.append((num, arq))
            except ValueError:
                continue  # Ignora se não for número válido

        if not numeros:
            print(f"[AVISO] Nenhum arquivo com número válido encontrado na pasta {pasta}")
            return None

        # Pega maior número
        maior_arquivo = max(numeros, key=lambda x: x[0])[1]

        # Monta caminho completo
        caminho_final = os.path.join(pasta, maior_arquivo)

        return caminho_final
    
    except Exception as e:
        print(f"[AVISO] Erro inesperado ao definir caminho: {e}")
        return None

import pandas as pd

def scrap_ajustes_bmf(data):

    caminho = definir_caminho_adj_bmf(data)

    return pd.read_csv(caminho, sep=";")
    
if __name__ == "__main__":
    print("uptodata_clients")