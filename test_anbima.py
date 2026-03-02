from dotenv import load_dotenv
load_dotenv()

from clients.anbima import AnbimaClient
from clients.anbima.endpoints import MERCADO_SECUNDARIO_TPF

client = AnbimaClient()

print("Testando Mercado Secundário TPF...")

date_list = ["2026-01-21", "2026-01-20", "2026-01-19", "2026-01-18"]
print(client.fetch_for_dates(MERCADO_SECUNDARIO_TPF, date_list))