# Golden files — calculos e API (baseline)

**Data base de referencia:** `2026-05-25`

JSON congelados a partir dos titulos, funcoes auxiliares e respostas HTTP (codigo pre-refatoracao).

## Regenerar

Calculos (titulospub):
```bash
python scripts/export_golden_calculos.py --force
```

Respostas HTTP (API):
```bash
python scripts/export_golden_api.py --force
```

Atualize estes arquivos apenas com justificativa explicita no PR.
