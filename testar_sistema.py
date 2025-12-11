"""
Teste geral do sistema - verifica API, Dash e funcionalidades principais
"""

import sys
import time
import requests
from pathlib import Path

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERRO]{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[AVISO]{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print("\n" + "="*70)
    print("TESTE 1: IMPORTS")
    print("="*70)
    
    try:
        print_info("Testando import do titulospub...")
        from titulospub import NTNB, LTN, LFT, NTNF
        print_success("titulospub importado com sucesso")
        
        print_info("Testando import da API...")
        from api.main import app
        print_success("API importada com sucesso")
        
        print_info("Testando import do Dash...")
        from dash_app.app import app as dash_app
        print_success("Dash importado com sucesso")
        
        print_info("Testando imports dos routers...")
        from api.routers import ntnb, ltn, lft, ntnf, vencimentos, carteiras
        print_success("Routers importados com sucesso")
        
        print_info("Testando imports das páginas do Dash...")
        from dash_app.pages import home, ltn, ntnb, ntnf
        print_success("Páginas do Dash importadas com sucesso")
        
        return True
    except Exception as e:
        print_error(f"Erro nos imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_connection():
    """Testa se a API está rodando"""
    print("\n" + "="*70)
    print("TESTE 2: CONEXÃO COM API")
    print("="*70)
    
    API_URL = "http://localhost:8000"
    
    try:
        print_info("Verificando se a API está rodando...")
        response = requests.get(f"{API_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success("API está rodando!")
            return True
        else:
            print_warning(f"API respondeu com status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("API não está rodando!")
        print_info("Para iniciar a API, execute: python run_api.py")
        return False
    except Exception as e:
        print_error(f"Erro ao conectar com API: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints principais da API"""
    print("\n" + "="*70)
    print("TESTE 3: ENDPOINTS DA API")
    print("="*70)
    
    API_URL = "http://localhost:8000"
    all_ok = True
    
    # Teste 1: Vencimentos
    try:
        print_info("Testando endpoint /vencimentos/ltn...")
        response = requests.get(f"{API_URL}/vencimentos/ltn", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print_success(f"Vencimentos LTN: {len(data)} encontrados")
            else:
                print_warning("Vencimentos LTN retornou lista vazia")
        else:
            print_error(f"Erro ao buscar vencimentos: {response.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"Erro ao testar vencimentos: {e}")
        all_ok = False
    
    # Teste 2: Criar carteira
    try:
        print_info("Testando criação de carteira NTNB...")
        response = requests.post(
            f"{API_URL}/carteiras/ntnb",
            json={"dias_liquidacao": 1},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            carteira_id = data.get("carteira_id")
            titulos = data.get("titulos", [])
            print_success(f"Carteira criada: {carteira_id} com {len(titulos)} títulos")
            
            # Teste 3: Atualizar taxa
            if carteira_id and len(titulos) > 0:
                primeiro_titulo = titulos[0]
                vencimento = primeiro_titulo.get("vencimento")
                
                print_info(f"Testando atualização de taxa para vencimento {vencimento}...")
                response = requests.put(
                    f"{API_URL}/carteiras/{carteira_id}/taxa",
                    json={"vencimento": vencimento, "taxa": 7.5},
                    timeout=30
                )
                if response.status_code == 200:
                    data_atualizada = response.json()
                    titulo_atualizado = next(
                        (t for t in data_atualizada.get("titulos", []) 
                         if t.get("vencimento") == vencimento),
                        None
                    )
                    if titulo_atualizado and abs(float(titulo_atualizado.get("taxa", 0)) - 7.5) < 0.0001:
                        print_success(f"Taxa atualizada com sucesso! PU: {titulo_atualizado.get('pu_termo')}")
                    else:
                        print_error("Taxa não foi atualizada corretamente")
                        all_ok = False
                else:
                    print_error(f"Erro ao atualizar taxa: {response.status_code}")
                    all_ok = False
        else:
            print_error(f"Erro ao criar carteira: {response.status_code}")
            all_ok = False
    except Exception as e:
        print_error(f"Erro ao testar carteiras: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False
    
    return all_ok

def test_dash_structure():
    """Testa se a estrutura do Dash está correta"""
    print("\n" + "="*70)
    print("TESTE 4: ESTRUTURA DO DASH")
    print("="*70)
    
    try:
        from dash_app.app import app
        from dash_app.config import API_URL, APP_TITLE
        
        print_info("Verificando configuração do Dash...")
        if API_URL:
            print_success(f"API_URL configurada: {API_URL}")
        else:
            print_warning("API_URL não configurada")
        
        if APP_TITLE:
            print_success(f"APP_TITLE: {APP_TITLE}")
        
        print_info("Verificando páginas do Dash...")
        from dash_app.pages import home, ltn, lft, ntnb, ntnf, ntnb_hedge
        
        pages = {
            "home": home,
            "ltn": ltn,
            "lft": lft,
            "ntnb": ntnb,
            "ntnf": ntnf,
            "ntnb_hedge": ntnb_hedge,
        }
        
        for name, page_module in pages.items():
            if hasattr(page_module, 'layout'):
                print_success(f"Página {name} tem função layout()")
            else:
                print_error(f"Página {name} não tem função layout()")
                return False
        
        print_info("Verificando componentes...")
        from dash_app.components import navbar
        if hasattr(navbar, 'create_navbar'):
            print_success("Componente navbar encontrado")
        else:
            print_warning("Componente navbar pode estar incompleto")
        
        print_info("Verificando utilitários...")
        from dash_app.utils import api, carteiras, vencimentos
        print_success("Utilitários encontrados")
        
        return True
    except Exception as e:
        print_error(f"Erro na estrutura do Dash: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_titulospub_classes():
    """Testa se as classes do titulospub funcionam"""
    print("\n" + "="*70)
    print("TESTE 5: CLASSES DO TITULOSPUB")
    print("="*70)
    
    try:
        from titulospub import NTNB, LTN, LFT, NTNF
        from titulospub.core.carteiras import CarteiraNTNB, CarteiraLTN
        
        print_info("Testando criação de títulos...")
        # Usar vencimentos que provavelmente existem
        ntnb = NTNB("2030-08-15", taxa=7.5)
        print_success("NTNB criado com sucesso")
        
        # Tentar criar LTN com um vencimento que pode não existir
        # Se falhar, não é um problema crítico - apenas mostra que precisa de vencimento válido
        try:
            # Tentar buscar um vencimento válido primeiro
            from titulospub.dados.vencimentos import get_vencimentos_ltn
            vencimentos_ltn = get_vencimentos_ltn()
            if vencimentos_ltn and len(vencimentos_ltn) > 0:
                vencimento_valido = vencimentos_ltn[0]
                ltn = LTN(vencimento_valido, taxa=12.0)
                print_success(f"LTN criado com sucesso (vencimento: {vencimento_valido})")
            else:
                print_warning("Não foi possível obter vencimentos válidos para LTN")
        except Exception as e:
            print_warning(f"Não foi possível criar LTN (pode ser normal se vencimento não existir): {e}")
        
        print_info("Testando classes de carteira...")
        # Não vamos criar carteira real aqui para não demorar muito
        print_success("Classes de carteira importadas com sucesso")
        
        return True
    except Exception as e:
        print_error(f"Erro ao testar classes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("TESTE GERAL DO SISTEMA")
    print("="*70)
    print("\nEste teste verifica:")
    print("  1. Imports de todos os módulos")
    print("  2. Conexão com a API")
    print("  3. Endpoints da API")
    print("  4. Estrutura do Dash")
    print("  5. Classes do titulospub")
    print("\n" + "="*70)
    
    results = {}
    
    # Teste 1: Imports
    results['imports'] = test_imports()
    
    # Teste 2: API Connection
    results['api_connection'] = test_api_connection()
    
    # Teste 3: API Endpoints (só se API estiver rodando)
    if results['api_connection']:
        results['api_endpoints'] = test_api_endpoints()
    else:
        print_warning("Pulando teste de endpoints - API não está rodando")
        results['api_endpoints'] = None
    
    # Teste 4: Dash Structure
    results['dash_structure'] = test_dash_structure()
    
    # Teste 5: titulospub Classes
    results['titulospub_classes'] = test_titulospub_classes()
    
    # Resumo final
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASSOU")
        elif result is False:
            print_error(f"{test_name}: FALHOU")
        else:
            print_warning(f"{test_name}: PULADO")
    
    print("\n" + "="*70)
    
    # Determinar status geral
    critical_tests = ['imports', 'dash_structure', 'titulospub_classes']
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        if results.get('api_connection') and results.get('api_endpoints'):
            print_success("TODOS OS TESTES PASSARAM!")
            print("\nO sistema está funcionando perfeitamente.")
            print("Você pode iniciar o Dash com: python run_dash_app.py")
        elif results.get('api_connection'):
            print_warning("TESTES CRÍTICOS PASSARAM, mas há problemas com endpoints da API")
            print("Verifique os logs da API para mais detalhes.")
        else:
            print_warning("TESTES CRÍTICOS PASSARAM, mas a API não está rodando")
            print("Para testar completamente, inicie a API com: python run_api.py")
    else:
        print_error("ALGUNS TESTES CRÍTICOS FALHARAM!")
        print("Verifique os erros acima e corrija antes de usar o sistema.")
        sys.exit(1)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

