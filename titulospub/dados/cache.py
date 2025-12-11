import os
import pickle

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_data")

def save_cache(data, filename):
    """Salva um objeto em um arquivo pickle na pasta de cache."""
    # Cria a pasta cache_data se não existir
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = os.path.join(CACHE_DIR, filename)
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def load_cache(filename):
    """Carrega um objeto de um arquivo pickle na pasta de cache. Retorna None se não existir."""
    filepath = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def clear_cache(filename):
    """Remove um arquivo de cache (pickle) da pasta de cache, se existir."""
    filepath = os.path.join(CACHE_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Gerenciador de cache (pickle)')
    parser.add_argument('action', choices=['save', 'load', 'clear'], help='Ação: save, load ou clear')
    parser.add_argument('filename', help='Nome do arquivo pkl de cache')
    parser.add_argument('--data', help='Arquivo pickle de origem para salvar (apenas para save)')
    args = parser.parse_args()

    import pickle
    if args.action == 'save':
        if not args.data:
            print('Para salvar, forneça --data com o caminho de um arquivo pickle de origem.')
        else:
            with open(args.data, 'rb') as f:
                data = pickle.load(f)
            save_cache(data, args.filename)
            print(f'Cache salvo em {args.filename}')
    elif args.action == 'load':
        data = load_cache(args.filename)
        if data is not None:
            print(f'Cache carregado de {args.filename}:')
            print(data)
        else:
            print(f'Arquivo {args.filename} não encontrado.')
    elif args.action == 'clear':
        clear_cache(args.filename)
        print(f'Cache {args.filename} removido (se existia).') 