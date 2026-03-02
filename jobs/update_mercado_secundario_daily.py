from __future__ import annotations

from datetime import date, timedelta

from clients.anbima import AnbimaClient
from clients.anbima.endpoints import MERCADO_SECUNDARIO_TPF
from clients.anbima.transformers import api_list_to_df

from db.connection import get_conn
from db.queries.datas import missing_dates_for_table
from db.services.transforms.mercado_secundario_transform import transform_mercado_secundario_df
from db.services.mercado_secundario_service import MercadoSecundarioService

from dotenv import load_dotenv
load_dotenv()


TABLE = "MERCADO_SECUNDARIO"
DATE_COL = "data_referencia"
START_IF_EMPTY = "2017-01-01"


def run() -> None:
    # 1) Descobrir datas faltantes no DB
    dates = missing_dates_for_table(
        table=TABLE,
        date_col=DATE_COL,
        default_start=START_IF_EMPTY,
        skip_weekends=True, # ok deixar True; feriados a API devolve 404
    )

    if not dates:
        print("[JOB] Nada a atualizar (DB já está no último dia).")
        return

    print(f"[JOB] Datas a processar: {dates[0]} .. {dates[-1]} ({len(dates)})")

    # 2) Buscar tudo de uma vez na API
    client = AnbimaClient()
    payloads = client.fetch_for_dates(MERCADO_SECUNDARIO_TPF, dates)

    # 3) Lista/JSON -> DF cru
    df_raw = api_list_to_df(payloads)
    if df_raw is None or df_raw.empty:
        print("[JOB] API retornou vazio.")
        return

    # 4) Transform do DB (contrato do banco)
    df_db = transform_mercado_secundario_df(df_raw)
    if df_db is None or df_db.empty:
        print("[JOB] DF pós-transform vazio.")
        return

    # 5) Persistir (idempotente)
    with get_conn() as conn:
        MercadoSecundarioService.persistir_df(df_db, conn)

    print(f"[JOB] OK: inseridos/atualizados {len(df_db)} registros.")


if __name__ == "__main__":
    run()
