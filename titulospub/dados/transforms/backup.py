"""Reexporta backups Excel estáticos (pacote ``titulospub.dados.backup``)."""

from titulospub.dados.backup.excel_static import (
    backup_anbimas,
    backup_bmf,
    backup_cdi,
    backup_feriados,
    backup_ipca_fechado,
    backup_ipca_proj,
)

__all__ = [
    "backup_anbimas",
    "backup_bmf",
    "backup_cdi",
    "backup_feriados",
    "backup_ipca_fechado",
    "backup_ipca_proj",
]
