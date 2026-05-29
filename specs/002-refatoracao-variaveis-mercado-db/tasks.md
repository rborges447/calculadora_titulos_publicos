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

## ⚠️ Regra absoluta: contratos DEVEM ser mantidos

Cada task abaixo troca **origem + tratamento** dos dados. **Não** troca o contrato público.

| Obrigatório em toda task | Proibido |
|--------------------------|----------|
| Retorno de `get_*()` idêntico ao Spec 001 §4 | Renomear métodos, chaves ou colunas consumidas |
| `pytest tests/ -m regression -v` verde ao final | Alterar `vencimentos.py`, títulos ou API para “adaptar” ao DB |
| Falha de teste → corrigir **adapter/normalização** | Falha de teste → mudar golden/fixture sem justificativa |
| Baseline `2026-05-25` como referência | Assumir que schema do DB “é o novo contrato” |

**Consumidor crítico:** [`titulospub/dados/vencimentos.py`](../../titulospub/dados/vencimentos.py) **não será alterado** nesta spec. Tasks **T-013** e **T-014** devem garantir que `get_anbimas()` e `get_bmf()` continuam compatíveis (ver checklist em cada task).

**Testes que validam contrato de vencimentos:**
- `tests/titulospub/dados/test_vencimentos_regressao.py`
- `tests/api/test_vencimentos_endpoint.py`
- Golden: `tests/fixtures/golden/vencimentos_baseline.json`

---

## Fase 0 — Infraestrutura

- [x] **T-001** Adicionar `brazilian_bonds_db` em dependências do projeto (`requirements.txt`: `-e ../brazil_fixed_income_analytics`, `python-dotenv`)
- [x] **T-002** Criar módulo `titulospub/dados/db_reader.py` — `load_dotenv(.env)`, factory do `reader` (lazy singleton); [`.env.example`](../../.env.example) versionado
- [x] **T-003** Documentar `BBDB_DATA_ROOT` / `BBDB_DB_PATH` no README, spec §7 e `.env.example`

---

## Fase 1 — `atualizar_tudo(data)` e propagação de data

- [x] **T-004** Refatorar `atualizar_tudo(self, data, verbose=True)` — **`data` obrigatória**; repassar a mesma `data` a todos os `get_*` com `force_update=True`
- [x] **T-005** Adicionar parâmetro opcional `data` em `get_cdi(data=None, force_update=False)` (hoje não existe)
- [x] **T-006** Regra global: quando `force_update=True`, exigir `data` nos métodos que leem por data (exceto `get_feriados`)
- [x] **T-007** Atualizar `api/main.py` lifespan e `POST /atualizar-mercado` para chamar `atualizar_tudo(data=...)` com data explícita (ex.: dia útil anterior ou parâmetro do endpoint)
- [x] **T-008** Verificar regressão API + core após T-004–T-007 (`pytest tests/ -m regression`)

> **DoD T-004–T-008:** suite Spec 001 verde; API continua respondendo com mocks/fixtures offline.

---

## Fase 2 — Refatoração por variável (origem → tratamento → contrato)

> Para cada task abaixo: substituir scraping/cache/backup pela leitura via `reader`, aplicar **tratamento documentado na seção "Tratamento"**, e **manter retorno idêntico** ao baseline Spec 001.  
> **Se o teste de regressão falhar, ajuste o adapter — não o contrato, não `vencimentos.py`, não os títulos.**

### T-009 — Feriados

- [x] **T-009** Refatorar `get_feriados`

**Fonte:** `reader.feriados.fetch_all()` (sem `data`) — coluna `data`, `ORDER BY data`

**Tratamento:**
- Schema bruto: DataFrame com coluna `data` (minúscula)
- Transform: [`transforms/feriados.py`](../../titulospub/dados/transforms/feriados.py) — `transform_feriados` (`pd.to_datetime` + `.dt.normalize()` → `list` de `pd.Timestamp`); leitura encapsulada em `feriados_from_db()`
- Fallback: nenhum (scraping/backup removidos deste método)
- Cache em memória (`self._feriados`) + pickle `feriados.pkl` em `force_update` / cache miss — inalterado

**Baseline:** `feriados.pkl` regenerado a partir do DB (**1263** itens). O pickle anterior tinha **1264** entradas por duplicata de `2079-04-21` ausente no DB (fonte correta).

**Contrato (DEVE manter):** `list` de `pd.Timestamp` normalizados; tamanho e datas iguais ao baseline `feriados.pkl`.

**Verificação:** `test_get_feriados_retorna_lista_com_tamanho_esperado` + suite regression.

---

### T-010 — IPCA dict

- [x] **T-010** Refatorar `get_ipca_dict`

**Fonte:** `reader.ipca_dict.fetch_on(data)` — 1 linha do gold `IPCA_DICT` (16 colunas)

**Tratamento:**
- [`transforms/ipca.py`](../../titulospub/dados/transforms/ipca.py) — `transform_ipca(df)`: remove metadados (`data_referencia`, `ref_month_*`, `usa_fechado`, `data_coleta_referencia`, `ipca_proj_data_coleta`, `inicio_mes_ipca`, `fim_mes_ipca`); rename snake_case → `IPCA_KEYS`; casts `ULTIMO_MES_IPCA` → `int`, demais → `float`
- Leitura encapsulada em `ipca_dict_from_db(data)` via `get_reader().ipca_dict.fetch_on`
- `inicio_fim_mes_ipca` mantida no mesmo módulo (consumida por NTN-B/DAP; inalterada)
- `force_update=True` exige `data` (`_require_data`); `atualizar_tudo(data)` propaga a mesma data
- Fallback: nenhum (scraping/backup removidos deste método); `ValueError` se `fetch_on` não retornar linha

**Mapeamento gold → contrato:**

| Coluna gold | Chave contrato |
|-------------|----------------|
| `ultimo_mes_ipca` | `ULTIMO_MES_IPCA` |
| `indice_ipca_data_base` | `INDICE_IPCA_DATA_BASE` |
| `indice_ipca_fechado_atual` | `INDICE_IPCA_FECHADO_ATUAL` |
| `indice_ipca_fechado_anterior` | `INDICE_IPCA_FECHADO_ANTERIOR` |
| `var_ipca_atual` | `VAR_IPCA_ATUAL` |
| `var_ipca_ant` | `VAR_IPCA_ANTERIOR` |
| `ipca_proj` | `IPCA_PROJ` |
| `ipca_usado` | `IPCA_USADO` |

**Contrato (DEVE manter):** `dict` com todas as chaves em `IPCA_KEYS` (`tests/conftest.py`); valores e tipos iguais ao baseline `ipca_dict.pkl`.

**Verificação:** testes Camada 1 (`test_get_ipca_dict_*`) + Camada 2 NTN-B/LFT + suite regression.

---

### T-011 — CDI

- [x] **T-011** Refatorar `get_cdi`

**Fonte:** `reader.cdi.fetch_on(data)` — 1 linha do gold `CDI` (colunas `data_referencia`, `cdi`)

**Tratamento:**
- [`transforms/cdi.py`](../../titulospub/dados/transforms/cdi.py) — `transform_cdi(df)`: extrai `float(df["cdi"].iloc[0])`; coluna `data_referencia` é metadado (não entra no contrato)
- Leitura encapsulada em `cdi_from_db(data)` via `get_reader().cdi.fetch_on`
- `force_update=True` exige `data` (`_require_data`); cache miss sem `data` usa `pd.Timestamp.today().normalize()` (mesmo padrão de IPCA)
- Fallback: nenhum (scraping/backup removidos deste método); `ValueError` se `fetch_on` não retornar linha

**Contrato (DEVE manter):** retorno `float`; valor igual ao baseline `cdi.pkl` (**14.4**) para `data=2026-05-25`.

**Verificação:** `test_get_cdi_retorna_float_igual_baseline` + suite regression.

---

### T-012 — VNA LFT

- [x] **T-012** Refatorar `get_vna_lft`

**Fonte:** `reader.vna.fetch_on(data)` — gold `vna` (3 linhas por data: LFT, NTN-B, NTN-C)

**Tratamento:**
- [`transforms/vna_lft.py`](../../titulospub/dados/transforms/vna_lft.py) — `transform_vna_lft(df)`: filtra `codigo_selic == 210100` (LFT), extrai `float(df["vna"].iloc[0])`; colunas `data_referencia`, `vna_ajustado` etc. são metadados (contrato usa `vna`, não `vna_ajustado`)
- Leitura encapsulada em `vna_lft_from_db(data)` via `get_reader().vna.fetch_on`
- `force_update=True` exige `data` (`_require_data`); cache miss sem `data` usa `pd.Timestamp.today().normalize()` (mesmo padrão de CDI)
- Fallback: nenhum (scraping removido deste método); `ValueError` se `fetch_on` não retornar linha ou LFT ausente

**Contrato (DEVE manter):** retorno `float`; valor igual ao baseline `vna_lft.pkl` (**19069.075129**) para `data=2026-05-25`.

**Verificação:** `test_get_vna_lft_*` + `test_lft_regressao` + `test_post_lft_*` API + suite regression.

---

### T-013 — ANBIMAs (mercado com liquidações)

- [ ] **T-013** Refatorar `get_anbimas`

**Fonte:** `reader.mercado_com_liquidacoes.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Mapear DataFrame bruto → formato esperado por `anbimas()` ou substituir `anbimas()` por normalizador DB-native
- [ ] Garantir dict com chaves **`LTN`, `NTN-B`, `NTN-F`, `LFT`** (nomes exatos, incluindo hífen)
- [ ] Colunas finais: **`TITULO`, `DATA`, `VENCIMENTO`, `ANBIMA`, `PU`** (`datetime64` + numéricos)
- [ ] Replicar regra de `data` (hoje: D-1 útil quando `data is None` — **obrigatório** para compatibilidade com `vencimentos.py`)
- [ ] Remover `scrap_anbimas` / `backup_anbimas` deste método

**Contrato (DEVE manter) — checklist `vencimentos.py`:**
- [ ] `get_anbimas()["LTN"|"LFT"|"NTN-B"|"NTN-F"]["VENCIMENTO"]` existe e é iterável
- [ ] `get_vencimentos_ltn()` == golden `vencimentos_baseline.json` → `"ltn"` (12 itens)
- [ ] `get_vencimentos_lft()` == golden → `"lft"` (17 itens)
- [ ] `get_vencimentos_ntnb()` == golden → `"ntnb"` (15 itens)
- [ ] `get_vencimentos_ntnf()` == golden → `"ntnf"` (6 itens)
- [ ] `test_get_anbimas_*` Camada 1 verde (`assert_frame_equal` vs pickles)

**Verificação:** testes Camada 1 ANBIMA + **`test_vencimentos_regressao`** + **`test_vencimentos_endpoint`** + suite regression.

---

### T-014 — BMF (ajustes DI/DAP)

- [ ] **T-014** Refatorar `get_bmf`

**Fonte:** `reader.ajustes_bmf.fetch_on(data)`

**Tratamento** *(preencher na implementação):*
- [ ] Mapear para dict `{DI: df, DAP: df}` com colunas **`DATA`, `DATA_VENCIMENTO`, `<DI|DAP>`, `ADJ`**
- [ ] Coluna de contrato DI deve chamar-se **`DI`** (não `TckrSymb` ou ticker bruto)
- [ ] Reutilizar lógica de [`transforms/bmf.py`](../../titulospub/dados/transforms/bmf.py) onde fizer sentido ou reimplementar sobre schema do DB
- [ ] Ordenação por `DATA_VENCIMENTO` ascendente
- [ ] Remover `ajustes_bmf` scraping / `scrap_bmf_net` / `backup_bmf` deste método

**Contrato (DEVE manter) — checklist `vencimentos.py`:**
- [ ] `get_bmf()["DI"]["DI"]` existe (coluna com mesmo nome da chave do dict)
- [ ] `len(get_codigos_di_disponiveis()) == 47` (baseline `vencimentos_baseline.json`)
- [ ] `test_get_bmf_*` Camada 1 verde (`assert_frame_equal` vs pickles)

**Verificação:** testes Camada 1 BMF + **`test_vencimentos_regressao`** (contagem DI) + hedge DI nos títulos + suite regression.

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
| **Contrato** | Outputs de `get_*` **idênticos** ao Spec 001 §4 para `data=2026-05-25`; consumidores (`vencimentos.py`, títulos, API) **sem alteração** |
| Regressão | `pytest tests/ -m regression -v` verde offline |
| PR | Um domínio por PR (feriados, ipca, cdi, …) |
| Tratamento | Seção "Tratamento" + checklist de contrato preenchidos no PR |
| API | `atualizar_tudo(data)` propagado |
| Falha | Corrigir adapter; **não** mudar contrato nem consumidores |

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
