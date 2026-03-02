import sqlite3
from pathlib import Path
from .config import DB_PATH

def get_conn(db_path=None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn