import os
import time
import pandas as pd

def definir_caminho_adj_bmf(data):

    """
    Versão modificada que busca o arquivo mais recente por data de modificação,
    não apenas pelo número no nome do arquivo.
    """
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

        # Busca o arquivo mais recente por data de modificação
        arquivos_com_data = []
        for arq in arquivos_filtrados:
            caminho_completo = os.path.join(pasta, arq)
            if os.path.exists(caminho_completo):
                mtime = os.path.getmtime(caminho_completo)
                arquivos_com_data.append((mtime, arq, caminho_completo))

        if not arquivos_com_data:
            print(f"[AVISO] Nenhum arquivo válido encontrado na pasta {pasta}")
            return None

        # Pega o arquivo com maior data de modificação (mais recente)
        arquivo_mais_recente = max(arquivos_com_data, key=lambda x: x[0])
        
        print(f"[INFO] Encontrados {len(arquivos_filtrados)} arquivos com prefixo {prefixo}")
        print(f"[INFO] Arquivo mais recente selecionado: {arquivo_mais_recente[1]}")
        print(f"[INFO] Data de modificação: {time.ctime(arquivo_mais_recente[0])}")

        return arquivo_mais_recente[2]  # Retorna caminho completo
    
    except Exception as e:
        print(f"[AVISO] Erro inesperado ao definir caminho: {e}")
        import traceback
        traceback.print_exc()
        return None

import pandas as pd

def scrap_ajustes_bmf(data):

    caminho = definir_caminho_adj_bmf(data)

    return pd.read_csv(caminho, sep=";")
    
if __name__ == "__main__":
    print("uptodata_clients")