# Tasks — Spec 001: Refatoração VariaveisMercado

Pequenas tarefas ordenadas para implementação incremental.  
Cada item deve ser um PR pequeno ou commit atômico. Marque `[x]` ao concluir.

**Comando de verificação contínua:** `pytest tests/ -m regression -v`

---

## Fase 0 — Preparação (infra mínima)

- [x] **T-001** Criar estrutura de pastas `tests/`, `tests/fixtures/variaveis_mercado/`, `tests/fixtures/golden/`
- [x] **T-002** Adicionar `tests/conftest.py` vazio com docstring explicando propósito da suite
- [x] **T-003** Registrar marcadores `regression` e `slow` em `pyproject.toml` (`[tool.pytest.ini_options]`)
- [ ] **T-004** Documentar no README (ou link para Spec 001) o comando `pytest tests/ -m regression`

---

## Fase 1 — Baseline (congelar estado atual)

- [x] **T-005** Script/notebook `scripts/export_variaveis_mercado_fixtures.py` que exporta todos os `get_*()` para pickle
- [x] **T-006** Exportar `feriados.pkl` a partir do cache atual ou backup
- [x] **T-007** Exportar `ipca_dict.pkl`
- [x] **T-008** Exportar `cdi.pkl`
- [x] **T-009** Exportar `anbimas.pkl` (dict de DataFrames)
- [x] **T-010** Exportar `bmf.pkl` (dict `DI`/`DAP`)
- [x] **T-011** Exportar `vna_lft.pkl` (se disponível; documentar skip se ausente)
- [x] **T-012** Commitar fixtures em `tests/fixtures/variaveis_mercado/` com `data_base=2026-05-25` documentada

---

## Fase 2 — Stub reutilizável

- [x] **T-013** Implementar helper `load_fixture(name: str)` em `tests/conftest.py`
- [x] **T-014** Implementar classe `VariaveisMercadoFixture` com `get_feriados`, `get_cdi`, `get_ipca_dict`
- [x] **T-015** Completar `VariaveisMercadoFixture` com `get_anbimas`, `get_bmf`, `get_vna_lft`
- [x] **T-016** Fixture pytest `vm_fixo` retornando instância de `VariaveisMercadoFixture`
- [x] **T-017** Fixture pytest `data_base_fixa` = `"2026-05-25"`

---

## Fase 3 — Camada 1: contrato VariaveisMercado

- [x] **T-018** Criar `tests/titulospub/dados/test_variaveis_mercado_contrato.py`
- [x] **T-019** Teste `test_get_feriados_retorna_lista_com_tamanho_esperado`
- [x] **T-020** Teste `test_get_cdi_retorna_float_igual_baseline`
- [x] **T-021** Teste `test_get_ipca_dict_chaves_e_tipos`
- [x] **T-022** Teste `test_get_anbimas_chaves_e_colunas` (`LTN`, `NTN-B`, `NTN-F`, `LFT`)
- [x] **T-023** Teste `test_get_anbimas_dataframes_iguais_baseline` (`assert_frame_equal` por título)
- [x] **T-024** Teste `test_get_bmf_chaves_di_dap_e_colunas`
- [x] **T-025** Teste `test_get_bmf_dataframes_iguais_baseline`
- [x] **T-026** Teste `test_get_vna_lft_estrutura` (ou `@pytest.mark.skip` com motivo documentado)
- [x] **T-027** Mock do pacote/lake nos testes de contrato (quando refatoração existir) — validar adapter, não rede

---

## Fase 4 — Camada 2: regressão de cálculos (titulospub)

- [x] **T-028** Script para gerar golden JSON de um cenário LTN (`data_base`, vencimento, taxa fixa)
- [x] **T-029** `tests/titulospub/core/test_ltn_regressao.py` — assert `pu_d0`, `dv01`, `hedge_di`
- [x] **T-030** Golden + teste regressão NTN-B (1 cenário)
- [x] **T-031** Golden + teste regressão NTN-F (1 cenário)
- [x] **T-032** Golden + teste regressão LFT (1 cenário)
- [x] **T-033** `tests/titulospub/dados/test_vencimentos_regressao.py` — listas de vencimentos estáveis
- [x] **T-034** Golden + teste regressão equivalência (1 cenário, se aplicável)
- [x] **T-035** Marcar todos os testes de cálculo com `@pytest.mark.regression`

---

## Fase 5 — Camada 3: regressão API

- [x] **T-036** Fixture `client` com `TestClient(app)` e lifespan desabilitado/no-op
- [x] **T-037** Fixture/patch global de `VariaveisMercado` → `VariaveisMercadoFixture` nos imports dos títulos
- [x] **T-038** `tests/api/test_ltn_endpoint.py` — POST `/titulos/ltn` vs golden JSON
- [x] **T-039** Teste POST `/titulos/ntnb`
- [x] **T-040** Teste POST `/titulos/ntnf`
- [x] **T-041** Teste POST `/titulos/lft`
- [x] **T-042** Teste GET/POST vencimentos (conforme rotas existentes)
- [x] **T-043** Teste POST equivalência
- [x] **T-044** Validar status codes de erro (422) não regrediram — 1 caso por router

---

## Fase 6 — Camada 4 e CI (opcional / posterior)

- [ ] **T-045** Teste smoke em `dash_app` mockando resposta HTTP da API (1 callback crítico)
- [ ] **T-046** Job CI executando `pytest tests/ -m "regression and not slow"`
- [ ] **T-047** CI dispara em paths: `titulospub/dados/**`, `titulospub/core/**`, `api/**`

---

## Fase 7 — Integração com refatoração (quando mexer no orquestrador)

- [ ] **T-048** Introduzir dependência do pacote/lake em `VariaveisMercado` mantendo interface pública
- [ ] **T-049** Rodar `pytest tests/ -m regression` — corrigir adapter até Camada 1 passar
- [ ] **T-050** Camada 2 verde — se falhar, investigar normalização vs fórmula
- [ ] **T-051** Camada 3 verde
- [ ] **T-052** Remover código morto (scraping/cache) **somente** após 3 suites verdes consecutivas
- [ ] **T-053** Atualizar Spec 001 status para **Implementado** e registrar desvios (se houver)

---

## Definição de pronto (DoD) por tarefa

- Teste passa localmente sem rede
- Nome do teste descreve comportamento (`test_get_bmf_retorna_di_e_dap_com_colunas_esperadas`)
- Fixtures/golden commitados ou gerados por script documentado
- Nenhum import de `dash_app` → `titulospub.dados` introduzido nos testes

---

## Ordem sugerida de execução

```
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → (refatorar) Fase 7 → Fase 6
```

**Checkpoint 1** (antes de refatorar): Fases 0–4 completas, baseline verde com código atual.  
**Checkpoint 2** (após refatorar): Fases 5 e 7 completas.  
**Checkpoint 3** (produto maduro): Fase 6 no CI.
