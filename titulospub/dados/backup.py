import pandas as pd

from titulospub.utils.datas import adicionar_dias_uteis, e_dia_util


def backup_cdi():
    cdi_df  = pd.read_excel(r"Z:\Chila\projetos\calculadora_titulos_publicos\titulospub\dados\backup_excel\cdi.xlsx")
    cdi_float = float(cdi_df.iloc[0,0])
    return cdi_float

def backup_ipca_proj():
    ipca_proj_df  = pd.read_excel(r"Y:\Applications_TulletPrebon\Applications\projetos-rendafixa\calculadora_titulos_publicos\titulospub\dados\backup_excel\ipca_proj.xlsx")
    ipca_proj_float = float(ipca_proj_df.iloc[0,0])
    return ipca_proj_float

def backup_feriados():
    feriados_df = pd.read_excel(r"Z:\Chila\projetos\calculadora_titulos_publicos\titulospub\dados\backup_excel\feriados.xlsx")
    feriados_df["Feriados"] = pd.to_datetime(feriados_df["FERIADOS"])
    feriados_list = feriados_df["FERIADOS"].tolist()
    return feriados_list

def backup_ipca_fechado():
    ipca_fechado_df = pd.read_excel(r"Y:\Applications_TulletPrebon\Applications\projetos-rendafixa\calculadora_titulos_publicos\titulospub\dados\backup_excel\ipca_fechado.xlsx")
    ipca_fechado_df["DATA"] = ipca_fechado_df["DATA"].astype(str)
    ipca_fechado_df["DATA_CODIGO"] = ipca_fechado_df["DATA_CODIGO"].astype(str)
    ipca_fechado_df["MEDIDA"] = ipca_fechado_df["MEDIDA"].astype(str)
    ipca_fechado_df["VALOR"] = ipca_fechado_df["VALOR"].astype(float)
    return ipca_fechado_df

def backup_anbimas():
    anbimas_df = pd.read_excel(r"Z:\Chila\projetos\calculadora_titulos_publicos\titulospub\dados\backup_excel\anbimas.xlsx")  
    anbimas_df = anbimas_df.drop(index=0)
    anbimas_df = anbimas_df[["Código SELIC", "Data de Vencimento", "Tx. Indicativas", "PU"]]

    titulos = {100000: "LTN",
               770100: "NTN-C",
               210100: "LFT",
               760199: "NTN-B",
               950199: "NTN-F"}

    anbimas_df["Código SELIC"] = anbimas_df["Código SELIC"].replace(titulos)

    colunas = {"Código SELIC": "TITULO",
               "Data de Vencimento": "VENCIMENTO",
               "Tx. Indicativas": "ANBIMA"}
    
    anbimas_df = anbimas_df.rename(columns=colunas)
    anbimas_df["DATA"] = pd.Timestamp.today().normalize()
    anbimas_df["VENCIMENTO"] = pd.to_datetime(anbimas_df["VENCIMENTO"])

    anbimas_df = anbimas_df[["TITULO", "DATA", "VENCIMENTO", "ANBIMA", "PU"]]
    anbimas_df = anbimas_df.reset_index(drop=True)

    anbimas_dict = {"LTN": anbimas_df[anbimas_df["TITULO"] == "LTN"].reset_index(drop=True),
                    "NTN-C": anbimas_df[anbimas_df["TITULO"] == "NTN-C"].reset_index(drop=True),
                    "LFT": anbimas_df[anbimas_df["TITULO"] == "LFT"].reset_index(drop=True),
                    "NTN-B": anbimas_df[anbimas_df["TITULO"] == "NTN-B"].reset_index(drop=True),
                    "NTN-F": anbimas_df[anbimas_df["TITULO"] == "NTN-F"].reset_index(drop=True)}

    return anbimas_dict


def backup_bmf():
    bmf_di_df = pd.read_excel(r"Z:\Chila\projetos\calculadora_titulos_publicos\titulospub\dados\backup_excel\bmf.xlsx",
                           sheet_name="DI")
    bmf_dap_df = pd.read_excel(r"Z:\Chila\projetos\calculadora_titulos_publicos\titulospub\dados\backup_excel\bmf.xlsx",
                           sheet_name="DAP")
    
    bmf_dict = {"DI": bmf_di_df, "DAP": bmf_dap_df}

    nomes = {
        "F": "01", "G": "02", "H": "03", "J": "04",
        "K": "05", "M": "06", "N": "07", "Q": "08",
        "U": "09", "V": "10", "X": "11", "Z": "12"
    }

    for nome, df in bmf_dict.items():
        df.columns = df.columns.str.strip().str.upper()
        if "VENCTO" in df.columns:
            if nome == "DI":
                df["DATA_VENCIMENTO"] = df["VENCTO"].astype(str).apply(
                    lambda x: f"20{x[1:]}-{nomes.get(x[0], x[0])}-01"
            )
                df[nome] = nome + str(1) + df["VENCTO"]
            else:
                df["DATA_VENCIMENTO"] = df["VENCTO"].astype(str).apply(
                    lambda x: f"20{x[1:]}-{nomes.get(x[0], x[0])}-15"
            )
                df[nome] = nome + str(1) + df["VENCTO"]

            df["DATA_VENCIMENTO"] = pd.to_datetime(df["DATA_VENCIMENTO"])

            df['DATA_VENCIMENTO'] = df['DATA_VENCIMENTO'].apply(
            lambda x: x if e_dia_util(x) else adicionar_dias_uteis(x, 1)
                                                                        )

            df["DATA"] = pd.Timestamp.today().normalize()
            df["ADJ"] = df["ÚLT. PREÇO"]

            colunas = ["DATA", "DATA_VENCIMENTO", nome, "ADJ"]

            df = df[colunas]
            bmf_dict[nome] = df

    return bmf_dict


if __name__ == "__main__":
    print("🔄 Testando funções de backup...")
    
    try:
        print("📊 Testando backup_cdi()...")
        cdi = backup_cdi()
        print(f"✅ CDI: {cdi}")
        
        print("📊 Testando backup_feriados()...")
        feriados = backup_feriados()
        print(f"✅ Feriados: {len(feriados)} registros")
        
        print("📊 Testando backup_ipca_fechado()...")
        ipca_fechado = backup_ipca_fechado()
        print(f"✅ IPCA fechado: {ipca_fechado.shape}")
        
        print("📊 Testando backup_ipca_proj()...")
        ipca_proj = backup_ipca_proj()
        print(f"✅ IPCA proj: {ipca_proj}")
        
        print("📊 Testando backup_anbimas()...")
        anbimas = backup_anbimas()
        print(f"✅ ANBIMAS: {len(anbimas)} tipos de títulos")
        for titulo, df in anbimas.items():
            print(f"  - {titulo}: {len(df)} registros")
        
        print("📊 Testando backup_bmf()...")
        bmf = backup_bmf()
        print(f"✅ BMF: {len(bmf)} tipos de contratos")
        for tipo, df in bmf.items():
            print(f"  - {tipo}: {len(df)} registros")
        
        print("✅ Todas as funções de backup funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()