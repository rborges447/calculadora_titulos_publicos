"""Factory do reader ``brazilian_bonds_db`` com paths via ``.env``."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from dotenv import load_dotenv

if TYPE_CHECKING:
    from app.database.readers.gold_reader import GoldReader

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env", override=False)

_lock = threading.Lock()
_reader: Optional["GoldReader"] = None


def get_repo_root() -> Path:
    """Raiz do lake/DB (``BBDB_DATA_ROOT`` ou raiz deste repositório)."""
    env = os.getenv("BBDB_DATA_ROOT")
    if env:
        return Path(env).resolve()
    return _REPO_ROOT


def get_db_path() -> Path:
    """Caminho do SQLite (``BBDB_DB_PATH`` ou ``<repo>/database/app.db``)."""
    env = os.getenv("BBDB_DB_PATH")
    if env:
        return Path(env).resolve()
    return get_repo_root() / "database" / "app.db"


def get_reader() -> "GoldReader":
    """Retorna ``GoldReader`` lazy singleton (thread-safe)."""
    global _reader
    if _reader is not None:
        return _reader
    with _lock:
        if _reader is None:
            import brazilian_bonds_db as bbdb

            path = get_db_path()
            if not path.is_file():
                raise FileNotFoundError(
                    f"SQLite do bbdb não encontrado: {path}. "
                    "Copie .env.example para .env, ajuste BBDB_DB_PATH e execute "
                    "bbdb.update(data_root=...) para materializar o banco."
                )
            _reader = bbdb.read_data(db_path=path)
    return _reader


def reset_reader() -> None:
    """Limpa o singleton (útil em testes de integração)."""
    global _reader
    with _lock:
        _reader = None
