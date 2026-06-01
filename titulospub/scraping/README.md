# Scraping — aquisição legada (`titulospub/scraping`)

Coleta dados de fontes públicas na internet (ANBIMA, UpToData, etc.). **Requer rede.**

## Uso no produto

- **Não** é importado por `titulospub/core/`, `api/` ou `dash_app/`.
- O orquestrador [`VariaveisMercado`](../dados/orquestrador.py) usa **`brazilian_bonds_db`** por padrão.
- Scraping entra apenas via:
  - transforms `*_scraping` em `titulospub/dados/transforms/`;
  - fallback opt-in: `VM_ALLOW_SCRAPING_FALLBACK=1` (ver [`resilience.py`](../dados/resilience.py));
  - script operacional [`scripts/export_backup_via_scraping.py`](../../scripts/export_backup_via_scraping.py).

## Funções principais

| Módulo | Funções |
|--------|---------|
| `anbima_scraping.py` | `scrap_cdi`, `scrap_feriados`, `scrap_proj_ipca`, `scrap_anbimas`, `scrap_vna_lft` |
| `uptodata_scraping.py` | `scrap_ajustes_bmf` |
| `bmf_net_scraping.py` | `scrap_bmf_net` |
| `sidra_scraping.py` | indicadores IBGE (legado) |

## Testes

A suite `pytest -m regression` **não** usa scraping (fixtures offline). Testes de integração com rede usam `@pytest.mark.slow`.
