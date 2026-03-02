import sqlite3
from typing import Optional

class TitulosPublicosRepo:
    @staticmethod
    def get_id(conn: sqlite3.Connection, tipo_titulo: str, data_vencimento: str) -> Optional[int]:
        row = conn.execute("""
            SELECT id
            FROM TITULOS_PUBLICOS
            WHERE tipo_titulo = ? AND data_vencimento = ?
        """, (tipo_titulo, data_vencimento)).fetchone()
        return int(row[0]) if row else None

    @staticmethod
    def get_or_create(conn: sqlite3.Connection, tipo_titulo: str, data_vencimento: str,
                      expressao=None, data_base=None, codigo_selic=None, codigo_isin=None,
                      status: str = "ATIVO") -> int:
        existing = TitulosPublicosRepo.get_id(conn, tipo_titulo, data_vencimento)
        if existing is not None:
            return existing

        cur = conn.execute("""
            INSERT INTO TITULOS_PUBLICOS (
            tipo_titulo, data_vencimento, expressao, data_base, codigo_selic, codigo_isin, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tipo_titulo, data_vencimento, expressao, data_base, codigo_selic, codigo_isin, status))
        return int(cur.lastrowid)

