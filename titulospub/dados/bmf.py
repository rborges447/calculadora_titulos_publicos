
import pandas as pd
from titulospub.scraping.uptodata_scraping import scrap_ajustes_bmf

def ajustes_bmf(data):
    df = scrap_ajustes_bmf(data)

    contratos = {
        "DI": "DI1",
        "DAP": "DAP"
    }

    resultado = {}

    for nome, prefixo in contratos.items():
        temp_df = df[df["TckrSymb"].fillna("").str.startswith(prefixo)][["RptDt", "XprtnDt", "TckrSymb", "AdjstdQtTax"]]
        temp_df = temp_df.rename(columns={
            "RptDt": "DATA",
            "XprtnDt": "DATA_VENCIMENTO",
            "TckrSymb": nome,
            "AdjstdQtTax": "ADJ"
        })

        temp_df["DATA"] = pd.to_datetime(temp_df["DATA"])
        temp_df["DATA_VENCIMENTO"] = pd.to_datetime(temp_df["DATA_VENCIMENTO"])
        temp_df = temp_df.sort_values(by="DATA_VENCIMENTO").reset_index(drop=True)

        resultado[nome] = temp_df

    return resultado


if __name__ == "__main__":
    print("🔄 Testando processamento BMF...")
    
    try:
        from titulospub.dados.backup import backup_bmf
        import pandas as pd
        
        print("📊 Carregando dados BMF de backup...")
        bmf_data = backup_bmf()
        print(f"✅ Dados carregados: {len(bmf_data)} tipos de contratos")
        
        print("📊 Processando dados BMF...")
        # Simulando uma data para teste
        data = pd.Timestamp.today().normalize()
        processed = ajustes_bmf(data)
        print(f"✅ Dados processados: {len(processed)} tipos de contratos")
        
        for tipo, df in processed.items():
            print(f"  - {tipo}: {len(df)} registros")
            if len(df) > 0:
                print(f"    Colunas: {list(df.columns)}")
                print(f"    Primeiro registro: {df.iloc[0].to_dict()}")
        
        print("✅ Processamento BMF funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()