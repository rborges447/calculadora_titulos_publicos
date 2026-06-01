"""Resiliência de leitura: DB primário, scraping opt-in se o banco falhar."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class DbUnavailable(Exception):
    """Indica falha de acesso ou dado ausente no ``brazilian_bonds_db``."""


def scraping_fallback_enabled() -> bool:
    """``VM_ALLOW_SCRAPING_FALLBACK=1`` habilita fallback via rede (opt-in)."""
    return os.getenv("VM_ALLOW_SCRAPING_FALLBACK", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def is_db_unavailable_error(exc: BaseException) -> bool:
    if isinstance(exc, DbUnavailable):
        return True
    if isinstance(exc, FileNotFoundError):
        return True
    if isinstance(exc, OSError):
        return True
    if isinstance(exc, ValueError):
        msg = str(exc).lower()
        if "sem dados no banco" in msg or "sqlite do bbdb" in msg:
            return True
    return False


def fetch_with_fallback(
    variable: str,
    from_db: Callable[..., T],
    from_scraping: Callable[..., T] | None,
    *,
    data: Any = None,
    allow_fallback: bool | None = None,
) -> T:
    """
    Tenta ``from_db``; se falhar por indisponibilidade do DB e fallback estiver
    habilitado, chama ``from_scraping`` (requer rede).
    """
    use_fallback = (
        scraping_fallback_enabled() if allow_fallback is None else allow_fallback
    )
    try:
        if data is None:
            return from_db()
        return from_db(data)
    except Exception as exc:
        if not use_fallback or from_scraping is None:
            raise
        if not is_db_unavailable_error(exc):
            raise
        print(
            f"[AVISO] VM fallback: scraping para {variable} "
            f"(DB indisponível: {type(exc).__name__}: {exc})"
        )
        if data is None:
            return from_scraping()
        return from_scraping(data)
