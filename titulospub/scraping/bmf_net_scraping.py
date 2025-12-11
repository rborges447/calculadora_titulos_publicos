#importando as bibliotecas
import pandas as pd
import json
import requests, json

def scrap_bmf_net():

    simbolos = ["DI1", "DAP"]

    bmf_dict = {}
    for simbolo in simbolos:
        url = requests.get(f"https://cotacao.b3.com.br/mds/api/v1/DerivativeQuotation/{simbolo}")

        #lendo o conteúdo da resposta
        text = url.text

        #carregando o conteúdo de resposta
        dados = json.loads(text)
        df = pd.json_normalize(dados['Scty'])

        if simbolo == "DI1":
            simbolo = "DI"
        
        bmf_dict[simbolo] = df
    
    return bmf_dict

if __name__ == "__main__":
    print("🔄 Testando scraping BMF Net...")
    
    try:
        # Executar o scraping
        bmf_dict = scrap_bmf_net()
        
        print("✅ Scraping concluído com sucesso!")
        print(f"📊 Tipos de contratos obtidos: {list(bmf_dict.keys())}")
        
        # Mostrar informações de cada DataFrame
        for tipo, df in bmf_dict.items():
            print(f"\n📈 {tipo}:")
            print(f"  - Registros: {len(df)}")
            print(f"  - Colunas: {list(df.columns)}")
            print(f"  - Primeiras linhas:")
            print(df.head(3).to_string())
            
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o scraping: {e}")
        import traceback
        traceback.print_exc()