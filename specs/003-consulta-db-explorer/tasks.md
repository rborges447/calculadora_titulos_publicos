# Tasks — Spec 003: Explorer de consultas ao banco (API + Dash)

Pequenas tarefas ordenadas para implementação incremental.  
Cada item deve ser um **PR pequeno**. Marque `[x]` ao concluir.

**Spec:** [`003-consulta-db-explorer.md`](003-consulta-db-explorer.md)

**Verificação obrigatória ao final de cada fase (e ao fechar a spec):**

```bash
pytest tests/ -m regression -v
```

**Regra:** esta spec **não** altera contratos de cálculo (Spec 001/002). Falha em regression → não mergear.

---

## ⚠️ Regras por task

| Obrigatório | Proibido |
|-------------|----------|
| Lógica de consulta só em `titulospub/dados/consultas_db/` | Lógica em `api/routers/consultas_db.py` |
| Dash só via HTTP (`dash_app/utils/api.py`) | `import titulospub` em `dash_app/` |
| Whitelist de tabela/coluna no catálogo | SQL ou colunas livres do cliente |
| CSV via `exportar_csv()` no domínio | CSV montado só no browser sem passar pela API |
| Testes novos com mock de `get_reader` | Depender de `app.db` nos testes `regression` |

---

## Fase 0 — Documentação e estrutura

- [x] **T-001** Criar pacote `titulospub/dados/consultas_db/` com `__init__.py`, `excecoes.py` (ex.: `TabelaDesconhecidaError`, `ColunasInvalidasError`, `BancoIndisponivelError`, `LimiteExportacaoError`)

**DoD:** pacote importável; exceções documentadas; sem implementação de consulta ainda.

---

## Fase 1 — Domínio: máscara e consulta

### T-002 — Catálogo (máscara)

- [x] **T-002** Implementar `catalogo.py` com `FonteConsulta` e registro das **12 fontes v1** (spec §4.2)

**Tratamento:**
- Colunas alinhadas ao schema gold v2 do `bbdb` (`app/database/schema.py` no repo irmão)
- Para `ipca_dict` e `mercado_com_liquidacoes`: validar colunas contra `reader.fetch_on` com DB de dev ou documentar lista explícita no código
- `listar_catalogo()` retorna lista de dicts serializáveis (sem tuplas opacas na API)

**Contrato:** cada `id` é único; `colunas_padrao ⊆ colunas`; `reader_attr` existe em `GoldReader`.

**Verificação:** teste unitário que percorre todas as fontes e valida consistência interna.

---

### T-003 — Serviço de consulta

- [x] **T-003** Implementar `servico.py` + `serializacao.py` — `consultar(...)`

**Tratamento:**
- Modo `range` → `fetch_range`; modo `snapshot` → `fetch_all` + filtro opcional por `coluna_data`
- Projeção de colunas; `limite_preview` default 5000; `truncado` e `total_linhas`
- Intervalo livre; ajuste à disponibilidade no SQLite (`disponibilidade.py`)
- `FileNotFoundError` → `BancoIndisponivelError`

**Verificação:** `tests/titulospub/dados/test_consultas_db.py` com mock de reader (DataFrame sintético).

---

### T-004 — Exportação CSV

- [x] **T-004** Implementar `exportar_csv(...)` em `servico.py` (ou módulo dedicado chamado pelo serviço)

**Tratamento:**
- Mesmo pipeline de leitura que `consultar`, sem truncar preview
- `limite_max_exportacao` (500_000 linhas)
- UTF-8 BOM, separador `,`, nome `{tabela}_{inicio}_{fim}.csv`
- Expor em `consultas_db/__init__.py`: `listar_catalogo`, `consultar`, `exportar_csv`

**Verificação:** teste que valida bytes CSV, header e número de linhas com mock.

---

## Fase 2 — API

- [x] **T-005** Adicionar modelos Pydantic em `api/models.py`: `ConsultaDbRequest`, `ConsultaHistoricoResponse`, `CatalogoConsultasResponse`, `ConsultasDbStatusResponse`

- [x] **T-006** Criar `api/routers/consultas_db.py` com endpoints:
  - `GET /consultas-db/catalogo`
  - `GET /consultas-db/status`
  - `POST /consultas-db/consultar`
  - `POST /consultas-db/exportar-csv`

**Tratamento:**
- Handlers delegam 1:1 ao domínio; mapeamento de exceções → 404/422/503
- Registrar router em `api/main.py`; atualizar payload de `GET /`

**Verificação:** `tests/api/test_consultas_db_endpoint.py` com `TestClient` e mock do módulo `consultas_db`.

---

## Fase 3 — Dash

- [x] **T-007** Estender `dash_app/utils/api.py` com `post_bytes(endpoint, payload, timeout=120)` para download CSV

- [x] **T-008** Criar `dash_app/pages/consultas_db.py`:
  - Dropdown tabela (catálogo)
  - Checklist colunas
  - DatePickerRange condicional
  - DataTable preview
  - Botão consultar → `POST /consultas-db/consultar`
  - Botão download → `POST /consultas-db/exportar-csv` + `dcc.Download`

- [x] **T-009** Registrar rota em `dash_app/app.py` e entrada em `dash_app/config.py` → `PAGES["consultas_db"]`

**Tratamento:**
- Mensagens de erro para 503 e `truncado=True`
- Aviso UI para tabelas de alto volume (range > 30 dias)

**Verificação:** smoke manual — API + Dash; sem import de `titulospub` no dash.

---

## Fase 4 — Documentação e fechamento

- [x] **T-010** Atualizar [`README.md`](../../README.md) — seção “Consultas ao banco” (rota Dash, endpoints, pré-requisito `app.db`)

- [x] **T-011** Gate final: `pytest tests/ -m regression -v` verde; revisar checklist da spec §10

**Opcional (não bloqueia v1):**

- [ ] **T-012** Testes de integração `pytest -m integration` com `app.db` local (marker separado)

---

## Resumo de dependências entre tasks

```text
T-001 → T-002 → T-003 → T-004 → T-005 → T-006 → T-007 → T-008 → T-009 → T-010 → T-011
                              └──────────────────┘
                                    (API após domínio)
```

---

## Checklist de aceite (spec §10)

- [x] Tela `/consultas-db` funcional
- [x] Escolha de tabela, colunas e range
- [x] Preview via API
- [x] CSV via API + domínio `exportar_csv`
- [x] Dash sem `titulospub`
- [x] Regression verde
