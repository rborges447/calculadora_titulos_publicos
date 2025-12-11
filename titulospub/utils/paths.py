import os

# Diretório base do projeto (pasta que contém o pacote titulospub)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def path_backup_csv(nome_arquivo: str) -> str:
    """
    Caminho completo para um arquivo dentro de backup_csv/
    """
    return os.path.join(BASE_DIR, "backup_csv", nome_arquivo)

def path_backup_pickle(nome_arquivo: str) -> str:
    """
    Caminho completo para um arquivo dentro de backup/ (pickle automático)
    """
    return os.path.join(BASE_DIR, "backup", nome_arquivo)

# (Opcional para futuro)
def path_logs(nome_arquivo: str) -> str:
    return os.path.join(BASE_DIR, "logs", nome_arquivo)
