import pandas as pd
from db.services.mercado_secundario_service import MercadoSecundarioService

df = pd.DataFrame([
{
"tipo_titulo": "LFT",
"data_vencimento": "2026-03-01",
"data_referencia": "2026-01-16",
"taxa_anbima": 0.0218,
"intervalo_min_d0": -0.0479,
"intervalo_max_d0": 0.0600,
"intervalo_min_d1": -0.0400,
"intervalo_max_d1": 0.0500,
"pu": 1000.0,
"expressao": "Rentabilidade (% a.a.)/252",
"codigo_selic": "210100",
"data_base": "2000-07-01",
}
])

MercadoSecundarioService.persistir_df(df)
print("OK inseriu")
