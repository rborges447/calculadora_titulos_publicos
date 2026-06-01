"""Paths para backups Excel estáticos."""

from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def get_backup_excel_dir() -> Path:
    """Diretório ``backup_excel`` (``BACKUP_EXCEL_DIR`` ou default no repo)."""
    env = os.getenv("BACKUP_EXCEL_DIR")
    if env:
        return Path(env).resolve()
    return _REPO_ROOT / "titulospub" / "dados" / "backup_excel"


def backup_excel_path(filename: str) -> Path:
    return get_backup_excel_dir() / filename
