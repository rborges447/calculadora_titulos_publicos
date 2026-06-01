# Backup estático (`titulospub/dados/backup`)

Funções de leitura de arquivos Excel em `titulospub/dados/backup_excel/` (ou `BACKUP_EXCEL_DIR`).

**Não** fazem parte do fluxo normal de `VariaveisMercado` (produção usa `brazilian_bonds_db`). Servem como último recurso operacional ou para comparar dados quando o SQLite não está disponível.

| Variável | Função |
|----------|--------|
| CDI | `backup_cdi()` |
| Feriados | `backup_feriados()` |
| IPCA proj / fechado | `backup_ipca_proj()`, `backup_ipca_fechado()` |
| ANBIMAs | `backup_anbimas()` |
| BMF | `backup_bmf()` |

Configuração: `BACKUP_EXCEL_DIR` no `.env` (ver `.env.example`).
