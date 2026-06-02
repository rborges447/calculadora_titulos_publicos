# Tasks — Spec 004: UX Consultas DB (formatação, tabela, CSV pt-BR)



Pequenas tarefas ordenadas para implementação incremental.  

Cada item deve ser um **PR pequeno**. Marque `[x]` ao concluir.



**Spec:** [`004-consulta-db-ux-formatacao.md`](004-consulta-db-ux-formatacao.md)



**Pré-requisito:** Spec 003 implementada (`/consultas-db` funcional).



**Verificação obrigatória ao final de cada fase (e ao fechar a spec):**



```bash

pytest tests/ -m regression -v

```



**Regra:** não alterar contratos de cálculo (Spec 001/002) nem payload HTTP da Spec 003.



---



## ⚠️ Regras por task



| Obrigatório | Proibido |

|-------------|----------|

| Locale pt-BR em `formatacao.py` (domínio) | Lógica de formatação CSV duplicada no Dash |

| Filtros/ocultar colunas só no client (Dash) | Novos query params de filtro na API |

| CSV via `exportar_csv()` atualizado | `import titulospub` em `dash_app/` |

| Testes unitários de formatação | Depender de `app.db` em `regression` |



---



## Fase 0 — Módulo de formatação (domínio)



- [x] **T-001** Criar `titulospub/dados/consultas_db/formatacao.py` com:

  - `formatar_numero_pt_br(valor, *, casas_decimais=None) -> str`

  - `formatar_data_exibicao(valor) -> str` (`DD/MM/YYYY`)

  - `formatar_dataframe_para_csv_pt_br(df) -> pd.DataFrame` (strings prontas para CSV)

  - Constantes `CSV_SEPARADOR_CAMPOS = ";"`, documentação de quoting



**DoD:** funções puras, sem I/O; docstrings curtas; tipos anotados.



**Verificação:** `tests/titulospub/dados/test_consultas_db_formatacao.py` (criar nesta task ou T-002).



---



## Fase 1 — CSV legível (domínio)



- [x] **T-002** Alterar `exportar_csv` em `servico.py`:

  - Aplicar `formatar_dataframe_para_csv_pt_br` antes da escrita

  - Separador `;`, UTF-8 BOM mantido

  - Datas `DD/MM/YYYY`; números com `.` milhar e `,` decimal

  - Quoting correto em campos texto com `;` ou `,`



- [x] **T-003** Atualizar `tests/titulospub/dados/test_consultas_db.py`:

  - `test_exportar_csv_bytes_e_bom`: header `data_referencia;cdi`, decimais com vírgula

  - Caso com string que contém `;` ou `,` (quoting)



**DoD:** CSV abre corretamente no Excel pt-BR (validação manual registrada no PR).



---



## Fase 2 — Dash: formatação na tabela



- [x] **T-004** Criar `dash_app/utils/formatacao_pt_br.py` (espelho da UI, sem importar `titulospub`) e usar em `consultas_db.py`:

  - `_formatar_rows_para_exibicao(colunas, rows)` → números e datas pt-BR na DataTable

  - Manter paridade com `formatacao.py` via **mesmos casos de teste** (fixtures compartilhadas ou tabela input/expected duplicada)



**Proibido:** `import titulospub` no Dash; novo campo `rows_formatados` na API (fora do escopo).



- [x] **T-005** Formatar metadados (`consultas-db-meta`, alertas de truncado) com milhar `.`.



**DoD:** preview numérico legível; datas `DD/MM/YYYY` na grade.



---



## Fase 3 — Dash: tabela interativa



- [x] **T-006** Estender `_montar_datatable`:

  - `filter_action="native"`

  - `sort_action="native"` (e `sort_mode` se útil)

  - Controle de colunas visíveis: `hidden_columns` + checklist `consultas-db-colunas-preview` **ou** `column_selectable` conforme UX escolhida



- [x] **T-007** Callback pós-consulta:

  - Popular checklist de colunas visíveis com `colunas_resp`

  - Sincronizar ocultação de colunas na DataTable

  - Texto de ajuda: filtros da tabela não afetam o CSV



**DoD:** usuário filtra e oculta coluna após consultar sem novo POST.



**Verificação:** smoke manual na página.



---



## Fase 4 — Documentação e fechamento



- [x] **T-008** Atualizar [`README.md`](../../README.md) — seção Consultas ao banco:

  - Formato numérico na UI (pt-BR)

  - CSV com separador `;` e Excel pt-BR

  - Filtros só no preview



- [x] **T-009** Gate final: `pytest tests/ -m regression -v` verde; checklist spec §8



**Opcional (não bloqueia):**



- [x] **T-010** Teste de contrato Dash: amostra de formatação igual ao domínio (mesmos inputs/outputs em JSON de fixture)



---



## Resumo de dependências entre tasks



```text

T-001 → T-002 → T-003 → T-004 → T-005 → T-006 → T-007 → T-008 → T-009

         └─ CSV domínio ─┘    └─ Dash UI ────────────────┘

```



---



## Checklist de aceite (spec §8)



- [x] Números na UI com `.` milhar e `,` decimal

- [x] Filtro por coluna na DataTable

- [x] Ocultar/exibir colunas no preview

- [x] CSV legível no Excel pt-BR (`;` + decimal `,`)

- [x] CSV só no domínio

- [x] Dash sem `titulospub`

- [x] Regression verde


