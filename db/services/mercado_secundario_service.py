import sqlite3

import pandas as pd
from db.connection import get_conn
from db.repositories.titulos_publicos_repo import TitulosPublicosRepo
from db.repositories.mercado_secundario_repo import MercadoSecundarioRepo

class MercadoSecundarioService:
    @staticmethod
    def persistir_df(df: pd.DataFrame, conn_or_db_path=None) -> None:
        """
        Persiste o DataFrame no banco de dados.
        
        Args:
            df: DataFrame com os dados do mercado secundário
            conn_or_db_path: Conexão SQLite existente ou caminho do banco (None = default)
        """
        # Se for uma conexão, usa diretamente; senão, cria uma nova
        if isinstance(conn_or_db_path, sqlite3.Connection):
            conn = conn_or_db_path
            should_close = False
        else:
            conn = get_conn(conn_or_db_path)
            should_close = True
        
        try:
            conn.execute("BEGIN;")

            for _, row in df.iterrows():
                titulo_id = TitulosPublicosRepo.get_or_create(
                    conn,
                    tipo_titulo=str(row["tipo_titulo"]),
                    data_vencimento=str(row["data_vencimento"]),
                    expressao=row.get("expressao"),
                    data_base=row.get("data_base"),
                    codigo_selic=row.get("codigo_selic"),
                    codigo_isin=row.get("codigo_isin"),
                    status="ATIVO",
                )

                MercadoSecundarioRepo.upsert(
                    conn,
                    titulo_id=titulo_id,
                    data_referencia=str(row["data_referencia"]),
                    taxa_anbima=row.get("taxa_anbima"),
                    intervalo_min_d0=row.get("intervalo_min_d0"),
                    intervalo_max_d0=row.get("intervalo_max_d0"),
                    intervalo_min_d1=row.get("intervalo_min_d1"),
                    intervalo_max_d1=row.get("intervalo_max_d1"),
                    pu=row.get("pu"),
                )

            conn.execute("COMMIT;")
        except Exception:
            conn.execute("ROLLBACK;")
            raise
        finally:
            if should_close:
                conn.close()


