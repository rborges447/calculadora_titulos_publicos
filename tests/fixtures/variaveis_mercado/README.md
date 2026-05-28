# Fixtures — VariaveisMercado (baseline)

**Data base de referência:** `2026-05-25`

Pickles congelados a partir de `VariaveisMercado.get_*()` (código pré-refatoração).
Usados pela suite de regressão da Spec 001.

## Regenerar baseline

```bash
python scripts/export_variaveis_mercado_fixtures.py --data-base 2026-05-25 --force
```

Requer rede e/ou arquivos em `titulospub/dados/backup_excel/`.

## Atualização

Só altere estes arquivos com **justificativa explícita** no PR (mudança intencional
de contrato ou correção de bug comprovada).

