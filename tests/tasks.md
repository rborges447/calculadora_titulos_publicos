# Tasks — Spec 002: Refatoração `VariaveisMercado` (banco local)

Pequenas tarefas ordenadas para implementação incremental.  
Cada item deve ser um **PR pequeno**. Marque `[x]` ao concluir.

**Verificação obrigatória ao final de cada task:**

```bash
pytest tests/ -m regression -v
```

**Data de referência baseline:** `2026-05-25`  
**Reader:** `brazilian_bonds_db.read_data(db_path=...)` (ver [`pacote_test.ipynb`](../../pacote_test.ipynb))

---

## Fase 0 — Infraestrutura

- [ ] **T-001** Adicionar `brazilian_bonds_db` em dependências do projeto (`requirements.txt` / `pyproject.toml`)
- [ ] **T-002** Criar módulo `titulospub/dados/db_reader.py` — factory do `reader` (`BBDB_DB_PATH`, lazy singleton)
- [ ] **T-003** Documentar variáveis de ambiente `BBDB_DATA_ROOT` / `BBDB_DB_PATH` (README ou spec)

---

## Fase 1 — `atualizar_tudo(data)` e propagação de data

- [ ] **T-004** Refatorar `atualizar_tudo(self, data, verbose=True)` — **`data` obrigatória**; repassar a mesma `data` a todos os `get_*` com `force_update=True`
- [ ] **T-005** Adicionar parâmetro opcional `data` em `get_cdi(data=None, force_update=False)` (hoje não existe)
- [ ] **T-006** Regra global: quando `force_update=True`, exigir `data` nos métodos que leem por data (exceto `get_feriados`)
- [ ] **T-007** Atualizar `api/main.py` lifespan e `POST /atualizar-mercado` para chamar `atualizar_tudo(data=...)` com data explícita (ex.: dia útil anterior ou parâmetro do endpoint)
- [ ] **T-008** Verificar regressão API + core após T-004–T-007 (`pytest tests/ -m regression`)

> **DoD T-004–T-008:** suite Spec 001 verde; API continua respondendo com mocks/fixtures offline.

---

## Fase 2 — Refatoração por variável (origem → tratamento → contrato)

> Para cada task abaixo: substituir scraping/cache/backup pela leitura via `reader`, aplicar **tratamento documentado na seção "Tratamento"**, manter retorno idêntico ao baseline Spec 001.

### T-009 — Feriados

- [ ] **T-009** Refatorar `get_feriados`

**Fonte:** `reader.feriados.fetch_all()` (sem `data`)

**Tratamento** *(preencher na implementação):*
- [ ] Inspecionar schema retornado por `fetch_all()` no notebook
- [ ] Normalizar para `list` de `pd.Timestamp` / `datetime` (mesmo tipo do baseline `feriados.pkl`)
- [ ] Remover dependência de `scrap_feriados` / `backup_feriados` neste método
- [ ] Manter cache em memória + comportamento `force_update`

**Verificação:** `test_get_feriados_retorna_lista_com_tamanho_esperado` + suite regression.

---

### T-010 — IPCA dict

- [ ] **T-010** Refatorar `get_ipca_dict`

**Fonte:** `reader.ipca_dict.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Mapear colunas do gold/silver `ipca_dict` → chaves do dict atual (`ULTIMO_MES_IPCA`, `INDICE_IPCA_DATA_BASE`, etc. — ver `IPCA_KEYS` em `tests/conftest.py`)
- [ ] Decidir se reutiliza `dicionario_ipca()` de [`ipca.py`](../../titulospub/dados/ipca.py) ou substitui por mapeamento direto do DB
- [ ] Garantir que `data` usada em `force_update` vem de `atualizar_tudo(data)` ou argumento explícito
- [ ] Fallback documentado se `fetch_on(data)` não retornar linha

**Verificação:** testes Camada 1 (`test_get_ipca_dict_*`) + Camada 2 NTN-B/LFT + suite regression.

---

### T-011 — CDI

- [ ] **T-011** Refatorar `get_cdi`

**Fonte:** `reader.cdi.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Extrair `float` único (taxa CDI) para a `data` informada
- [ ] Documentar coluna/campo usado no DB
- [ ] Usar `data` quando `force_update=True`
- [ ] Remover `scrap_cdi` / `backup_cdi` deste método

**Verificação:** `test_get_cdi_retorna_float_igual_baseline` + suite regression.

---

### T-012 — VNA LFT

- [ ] **T-012** Refatorar `get_vna_lft`

**Fonte:** `reader.vna.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Filtrar linha LFT / `codigo_selic` correto no DataFrame retornado
- [ ] Extrair `float` consumido por `LFT` (campo `vna` ou `vna_ajustado` — validar vs baseline `vna_lft.pkl`)
- [ ] Usar `data` em `force_update`
- [ ] Remover `scrap_vna_lft` deste método

**Verificação:** `test_get_vna_lft_*` + `test_lft_regressao` + `test_post_lft_*` API + suite regression.

---

### T-013 — ANBIMAs (mercado com liquidações)

- [ ] **T-013** Refatorar `get_anbimas`

**Fonte:** `reader.mercado_com_liquidacoes.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Mapear DataFrame bruto → formato esperado por `anbimas()` ou substituir `anbimas()` por normalizador DB-native
- [ ] Garantir dict com chaves `LTN`, `NTN-B`, `NTN-F`, `LFT`
- [ ] Colunas finais: `TITULO`, `DATA`, `VENCIMENTO`, `ANBIMA`, `PU` (`datetime64` + numéricos)
- [ ] Replicar regra de `data` (hoje: D-1 útil quando `data is None` — decidir se mantém ou usa `data` explícita de `atualizar_tudo`)
- [ ] Remover `scrap_anbimas` / `backup_anbimas` deste método

**Verificação:** testes Camada 1 ANBIMA + `test_vencimentos_regressao` + suite regression.

---

### T-014 — BMF (ajustes DI/DAP)

- [ ] **T-014** Refatorar `get_bmf`

**Fonte:** `reader.ajustes_bmf.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Mapear para dict `{DI: df, DAP: df}` com colunas `DATA`, `DATA_VENCIMENTO`, `<DI|DAP>`, `ADJ`
- [ ] Reutilizar lógica de [`bmf.py`](../../titulospub/dados/bmf.py) onde fizer sentido ou reimplementar sobre schema do DB
- [ ] Ordenação por `DATA_VENCIMENTO` ascendente
- [ ] Remover `ajustes_bmf` scraping / `scrap_bmf_net` / `backup_bmf` deste método

**Verificação:** testes Camada 1 BMF + hedge DI nos títulos + suite regression.

---

### T-015 — PTAX (novo)

- [ ] **T-015** Implementar `get_ptax(data=None, force_update=False)`

**Fonte:** `reader.ptax.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Definir tipo de retorno (ex.: `dict` com `ptax_compra`/`ptax_venda`, ou `float` único)
- [ ] Documentar consumidores futuros (nenhum hoje — não quebrar regressão existente)
- [ ] Adicionar teste de contrato mínimo em `tests/titulospub/dados/` (opcional nesta task se sem consumidor)
- [ ] Incluir em `atualizar_tudo(data)` se aplicável

**Verificação:** suite regression existente continua verde; novo teste de contrato se criado.

---

### T-016 — Leilões (novo)

- [ ] **T-016** Implementar `get_leiloes(data=None, force_update=False)`

**Fonte:** `reader.leiloes.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Definir tipo de retorno (ex.: `pd.DataFrame` com colunas documentadas)
- [ ] Documentar consumidores futuros
- [ ] Adicionar teste de contrato mínimo (opcional)
- [ ] Incluir em `atualizar_tudo(data)` se aplicável

**Verificação:** suite regression existente continua verde; novo teste de contrato se criado.

---

## Fase 3 — Testes e baseline

- [ ] **T-017** Atualizar `patch_variaveis_mercado_io` / fixtures se mocks precisarem simular `reader` em vez de scraping
- [ ] **T-018** Rodar `scripts/export_variaveis_mercado_fixtures.py` pós-refatoração — comparar diff; atualizar pickles **somente** se normalização intencional
- [ ] **T-019** Rodar `scripts/export_golden_calculos.py --force` e `export_golden_api.py --force` — validar se golden permanecem estáveis com `data=2026-05-25`
- [ ] **T-020** Marcar Spec 001 Fase 7 (T-048–T-053) como concluída

---

## Fase 4 — Limpeza (somente após Fase 2 + Fase 3 verdes)

- [ ] **T-021** Remover imports de scraping não usados do orquestrador
- [ ] **T-022** Deprecar/remover escrita de pickles em `cache_data/` (manter `limpar_cache` compatível)
- [ ] **T-023** Remover ou isolar módulos `titulospub/scraping/*` não referenciados (PR separado, revisão manual)
- [ ] **T-024** Atualizar Spec 002 status para **Implementado**; registrar desvios vs baseline

> **Gate T-021–T-024:** 3 execuções consecutivas de `pytest tests/ -m regression` verdes antes de merge.

---

## Definição de pronto (DoD) — resumo

| Item | Critério |
|------|----------|
| Contrato | Outputs de `get_*` iguais ao Spec 001 §4 para `data=2026-05-25` |
| Regressão | `pytest tests/ -m regression -v` verde offline |
| PR | Um domínio por PR (feriados, ipca, cdi, …) |
| Tratamento | Seção "Tratamento" da task preenchida no PR description |
| API | `atualizar_tudo(data)` propagado |

---

## Ordem sugerida de execução

```
Fase 0 → Fase 1 (data/atualizar_tudo) → Fase 2:
  T-009 feriados
  → T-011 cdi
  → T-010 ipca (depende feriados)
  → T-012 vna_lft
  → T-013 anbimas
  → T-014 bmf
  → T-015 ptax
  → T-016 leiloes
→ Fase 3 (baseline/testes)
→ Fase 4 (limpeza)
```

**Checkpoint 1:** Fase 1 completa — `atualizar_tudo(data)` + API, suite verde.  
**Checkpoint 2:** Fase 2 completa — todos os `get_*` no DB, suite verde.  
**Checkpoint 3:** Fase 4 — scraping removido, Spec 002 fechada.

---

## Mapeamento Spec 001 Fase 7 → Spec 002

| Spec 001 | Spec 002 |
|----------|----------|
| T-048 Introduzir dependência lake/DB | T-001, T-002 |
| T-049 Camada 1 verde | T-009–T-016 (cada task) |
| T-050 Camada 2 verde | idem |
| T-051 Camada 3 verde | T-004–T-008 + idem |
| T-052 Remover código morto | T-021–T-023 |
| T-053 Atualizar spec | T-024, T-020 |
