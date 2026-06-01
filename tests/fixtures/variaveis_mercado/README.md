# Fixtures — VariaveisMercado (baseline)

**Data base de referência:** `2026-05-25`

Pickles congelados a partir de `VariaveisMercado.get_*()` lendo `brazilian_bonds_db`.
Usados pela suite de regressão da Spec 001 / Spec 002.

## Regenerar baseline

```bash
python scripts/export_variaveis_mercado_fixtures.py --data-base 2026-05-25 --force
```

Requer `database/app.db` materializado (``BBDB_DB_PATH`` ou default na raiz do repo).

## Atualização

Só altere estes arquivos com **justificativa explícita** no PR (mudança intencional
de contrato ou correção de bug comprovada).

