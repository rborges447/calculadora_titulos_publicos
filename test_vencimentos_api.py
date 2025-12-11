"""
Script para testar os endpoints de vencimentos da API.
"""
import requests
import json
from datetime import datetime

# URL da API
API_URL = "http://localhost:8000"

def testar_endpoint(endpoint, nome):
    """Testa um endpoint específico"""
    print(f"\n{'='*60}")
    print(f"Testando: {nome}")
    print(f"Endpoint: {endpoint}")
    print('='*60)
    
    try:
        url = f"{API_URL}{endpoint}"
        print(f"URL completa: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            
            if isinstance(dados, list):
                print(f"Tipo: Lista")
                print(f"Total de itens: {len(dados)}")
                
                if len(dados) > 0:
                    print(f"\nPrimeiros 5 itens:")
                    for i, item in enumerate(dados[:5], 1):
                        print(f"  {i}. {item}")
                    
                    if len(dados) > 5:
                        print(f"\nUltimos 5 itens:")
                        for i, item in enumerate(dados[-5:], 1):
                            print(f"  {len(dados)-5+i}. {item}")
                else:
                    print("AVISO: Lista vazia!")
            elif isinstance(dados, dict):
                print(f"Tipo: Dicionario")
                print(f"Chaves: {list(dados.keys())}")
                print(f"\nConteudo:")
                print(json.dumps(dados, indent=2, ensure_ascii=False))
            else:
                print(f"Tipo: {type(dados)}")
                print(f"Conteudo: {dados}")
            
            print(f"\n[OK] Endpoint funcionando corretamente!")
            return True
            
        else:
            print(f"[ERRO] Status code: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[ERRO] Nao foi possivel conectar a API em {API_URL}")
        print("Certifique-se de que a API esta rodando (python run_api.py)")
        return False
    except requests.exceptions.Timeout:
        print(f"[ERRO] Timeout ao conectar a API")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Funcao principal"""
    print("\n" + "="*60)
    print("TESTE DE ENDPOINTS DE VENCIMENTOS - API")
    print("="*60)
    print(f"API URL: {API_URL}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Testar health check primeiro
    print("\n" + "="*60)
    print("1. Testando Health Check")
    print("="*60)
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("[OK] API esta respondendo!")
            print(f"Resposta: {response.json()}")
        else:
            print(f"[AVISO] Health check retornou status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] Nao foi possivel conectar a API: {e}")
        print("\nCertifique-se de que a API esta rodando:")
        print("  python run_api.py")
        return
    
    # Verificar se os endpoints estão disponíveis na documentação
    print("\n" + "="*60)
    print("2. Verificando Documentacao da API")
    print("="*60)
    try:
        response = requests.get(f"{API_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("[OK] Documentacao disponivel em:")
            print(f"  {API_URL}/docs")
            print("\nSe os endpoints retornarem 404, reinicie a API:")
            print("  1. Pare a API (Ctrl+C)")
            print("  2. Execute novamente: python run_api.py")
    except:
        pass
    
    # Lista de endpoints para testar
    endpoints = [
        ("/vencimentos/ltn", "Vencimentos LTN"),
        ("/vencimentos/lft", "Vencimentos LFT"),
        ("/vencimentos/ntnb", "Vencimentos NTNB"),
        ("/vencimentos/ntnf", "Vencimentos NTNF"),
        ("/vencimentos/di", "Codigos DI"),
        ("/vencimentos/todos", "Todos os Vencimentos"),
    ]
    
    resultados = []
    
    # Testar cada endpoint
    for endpoint, nome in endpoints:
        sucesso = testar_endpoint(endpoint, nome)
        resultados.append((nome, sucesso))
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    for nome, sucesso in resultados:
        status = "[OK]" if sucesso else "[FALHOU]"
        print(f"{status} {nome}")
    
    total_ok = sum(1 for _, sucesso in resultados if sucesso)
    total_testes = len(resultados)
    
    print(f"\nTotal: {total_ok}/{total_testes} testes passaram")
    
    if total_ok == total_testes:
        print("\n[SUCESSO] Todos os endpoints estao funcionando!")
    else:
        print(f"\n[ATENCAO] {total_testes - total_ok} endpoint(s) falharam")


if __name__ == "__main__":
    main()

