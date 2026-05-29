# Spec 001 — Refatoração VariaveisMercado

| Campo        | Valor                                      |
|--------------|--------------------------------------------|
| **ID**       | SPEC-001                                   |
| **Título**   | Fluxo de testes automatizados para refatoração de `VariaveisMercado` |
| **Status**   | Proposta                                   |
| **Autor**    | Rafael                                     |
| **Criado**   | 2026-05-26                                 |
| **Escopo**   | `titulospub`, `api`, `dash_app` (indireto) |
| **Fase atual** | **Somente criação da suite de testes** — sem refatoração |

---

## ⚠️ Restrição absoluta desta task

> **Em hipótese alguma esta task deve modificar código de produção.**

O objetivo desta spec, **neste momento**, é **estritamente criar a infraestrutura e os testes de regressão**. Nada além disso.

### O que é permitido criar ou alterar

| Permitido | Exemplos |
|-----------|----------|
| Código de teste | `tests/**`, `tests/conftest.py`, `tests/**/test_*.py` |
| Fixtures e golden files | `tests/fixtures/**` |
| Scripts auxiliares de baseline | `scripts/export_variaveis_mercado_fixtures.py` (somente exportação) |
| Configuração de testes | Marcadores pytest em `pyproject.toml` **apenas** na seção `[tool.pytest.ini_options]` |
| Documentação | `specs/**`, trecho mínimo no README sobre como rodar os testes |

### O que é proibido nesta task

| Proibido | Exemplos |
|----------|----------|
| Refatorar `VariaveisMercado` | `titulospub/dados/orquestrador.py` |
| Integrar pacote/lake/DB | Qualquer alteração em `titulospub/dados/*` de produção |
| Alterar títulos, cálculos ou API | `titulospub/core/**`, `api/**`, `dash_app/**` |
| “Aproveitar” para corrigir bugs | Mesmo que um teste exponha falha no código atual |
| Alterar fórmulas, contratos ou rotas | Mudanças de comportamento em código existente |

Se um teste **falhar** porque o código atual tem bug ou limitação conhecida:

1. Documentar o comportamento observado no teste (skip com motivo, ou xfail com issue).
2. **Não** alterar o código de produção para “fazer passar”.
3. A correção do código fica para **outra spec/PR**, após a suite estar verde contra o baseline.

A refatoração de `VariaveisMercado` (lake, pacote de dados, novo adapter) será uma **task futura**, separada, que **só começa** quando esta suite existir e estiver estável contra o código atual.

---

## 1. Contexto

A classe `VariaveisMercado` (`titulospub/dados/orquestrador.py`) é o orquestrador central de dados de mercado. Hoje ela obtém informações via scraping, cache local (`titulospub/dados/cache_data/*.pkl`) e backups estáticos.

A refatoração prevê substituir (total ou parcialmente) essa cadeia por um **novo pacote de dados** (lake/parquet/DB), mantendo o **mesmo contrato público** consumido por:

- Títulos: `LTN`, `LFT`, `NTN-B`, `NTN-F`, `DI`, `DAP`
- Carteiras: `carteira_ltn`, `carteira_lft`, `carteira_ntnb`, `carteira_ntnf`
- Utilitários: `titulospub/dados/vencimentos.py`, `titulospub/utils/carregamento_var_globais.py`
- API: startup (`lifespan`) e endpoint `/atualizar-mercado`
- Dash: consumo indireto via HTTP (sem import de `titulospub`)

**Problema:** não existe suite de testes automatizada hoje. Qualquer mudança em `VariaveisMercado` pode alterar silenciosamente PU, DV01, hedge, vencimentos e respostas da API.

**Objetivo desta spec (fase atual):** **implementar** um fluxo de testes de regressão reproduzível, rápido e independente de rede/scraping — para ser executado **antes e depois** de qualquer futura mudança em `VariaveisMercado`.

**Objetivo futuro (fora desta task):** usar essa suite para validar a refatoração quando ela for feita em spec/PR dedicado.

---

## 2. Objetivos

### 2.1 Objetivos desta task (somente testes)

1. **Criar** a estrutura `tests/` com fixtures, stubs e golden files.
2. **Criar** testes que documentem e congelem o comportamento **atual** do sistema (baseline).
3. **Criar** testes executáveis localmente e em CI **sem modificar** `titulospub`, `api` ou `dash_app`.
4. Garantir que a suite rode em **tempo previsível** (< 2 min), sem rede no CI.

### 2.2 Objetivos da suite (validação futura — não implementar agora)

Estes objetivos descrevem **para que** os testes servirão depois; **não** são escopo de alteração de código nesta task:

1. Detectar mudanças na **interface pública** de `VariaveisMercado`.
2. Detectar mudanças nos **outputs de cada `get_*()`** em relação ao baseline.
3. Detectar regressões em **cálculos** e **respostas da API**.

---

## 3. Fora de escopo

### 3.1 Proibido nesta task (código de produção)

- **Qualquer modificação** em `titulospub/`, `api/`, `dash_app/` (exceto leitura para entender contratos).
- Refatoração de `VariaveisMercado` ou integração com lake/pacote de dados.
- Alterar fórmulas financeiras ou comportamento de cálculo dos títulos.
- Corrigir bugs encontrados durante a escrita dos testes (registrar com skip/xfail; corrigir em PR separado).
- Adicionar injeção de dependência, hooks ou refactors “para facilitar o teste” no código de produção.

### 3.2 Fora de escopo geral da spec de testes

- Testes E2E completos do Dash (browser/UI).
- Testes de performance/carga (~100 usuários simultâneos).
- Validação de qualidade dos dados de mercado em produção (freshness, SLA de scraping).
- Implementar o adapter lake/DB (spec futura de refatoração).

---

## 4. Contrato público de `VariaveisMercado`

Métodos que devem ser cobertos:

| Método              | Retorno esperado (contrato)                                      | Consumidores principais        |
|---------------------|------------------------------------------------------------------|----------------------------------|
| `get_feriados()`    | `list` de datas (`datetime`/`Timestamp`)                         | Todos os títulos, datas utils    |
| `get_ipca_dict()`   | `dict` com chaves usadas em NTN-B / IPCA                         | NTN-B, LFT, utils                |
| `get_cdi()`         | `float`                                                          | LTN, NTN-F, carteiras            |
| `get_anbimas()`     | `dict[str, pd.DataFrame]` com chaves `LTN`, `NTN-B`, `NTN-F`, `LFT` | Títulos, vencimentos         |
| `get_bmf()`         | `dict[str, pd.DataFrame]` com chaves `DI`, `DAP`                 | LTN, NTN-F, NTN-B, vencimentos   |
| `get_vna_lft()`     | Estrutura consumida por `LFT`                                    | LFT, carteira_lft                |
| `atualizar_tudo()`  | Orquestra todos os `get_*` com `force_update=True`               | API startup, admin               |
| `limpar_cache()`    | Reseta estado interno + arquivos de cache                          | Manutenção                       |

### 4.1 Esquema mínimo — `get_anbimas()`

Cada DataFrame deve conter (após processamento `anbimas()`):

- Colunas: `TITULO`, `DATA`, `VENCIMENTO`, `ANBIMA`, `PU`
- `VENCIMENTO` e `DATA` como `datetime64`
- `ANBIMA` e `PU` como numéricos

### 4.2 Esquema mínimo — `get_bmf()`

Cada DataFrame (`DI`, `DAP`) deve conter:

- Colunas: `DATA`, `DATA_VENCIMENTO`, `<DI|DAP>`, `ADJ`
- Datas como `datetime64`
- `ADJ` numérico
- Ordenação por `DATA_VENCIMENTO` ascendente

---

## 5. Estratégia de testes (4 camadas)

```
Camada 1 — Contrato VariaveisMercado     (rápida, isolada)
    ↓
Camada 2 — Regressão titulospub          (cálculos com VM fixa)
    ↓
Camada 3 — Regressão API                 (TestClient + VM fixa)
    ↓
Camada 4 — Smoke Dash                    (opcional, mock HTTP)
```

### Camada 1 — Contrato (`tests/titulospub/dados/`)

- Instanciar `VariaveisMercado` com **fonte de dados mockada** (fixtures locais).
- Comparar output de cada `get_*()` com baseline congelado.
- Validar tipos, chaves, colunas, shape e valores.
- Usar `pd.testing.assert_frame_equal` para DataFrames.
- **Proibido:** scraping, rede, leitura de lake em tempo real no CI.

### Camada 2 — Regressão de cálculos (`tests/titulospub/core/`)

- Usar `VariaveisMercadoFixture` (stub) carregando fixtures de `tests/fixtures/`.
- Injetar via parâmetro `variaveis_mercado=` (já suportado pelos títulos).
- Inputs fixos: `data_base`, vencimentos, taxas explícitas quando possível.
- Comparar outputs numéricos com arquivos golden JSON (`pytest.approx`).
- Cobrir no mínimo um cenário por tipo de título + vencimentos + equivalência.

### Camada 3 — API (`tests/api/`)

- `fastapi.testclient.TestClient` sobre `api.main:app`.
- `patch` de `VariaveisMercado` nos pontos de import dos títulos ou do orquestrador.
- Desabilitar `lifespan` de atualização de mercado nos testes (no-op).
- POST nos endpoints principais; comparar JSON de resposta com golden.
- Endpoints mínimos: `/titulos/ltn`, `/titulos/lft`, `/titulos/ntnb`, `/titulos/ntnf`, `/vencimentos/*`, `/equivalencia`.

### Camada 4 — Dash (opcional)

- Testar apenas clientes HTTP em `dash_app/` (payload montado, parsing de resposta).
- Não repetir cálculos financeiros — confiar na Camada 3.

---

## 6. Fixtures e baseline

### 6.1 Diretório

```
tests/
  conftest.py
  fixtures/
    variaveis_mercado/
      feriados.pkl
      ipca_dict.pkl
      cdi.pkl
      anbimas.pkl
      bmf.pkl
      vna_lft.pkl
    golden/
      ltn_2027_taxa_12_5.json
      ntnb_2035_taxa_7_0.json
      ...
      api_ltn_response.json
```

### 6.2 Data de referência fixa

Todos os testes usam **`data_base = "2026-05-25"`**, alinhada ao partition `lake/silver/ajustes_bmf/data=2026-05-25`.

### 6.3 Geração do baseline (one-shot, antes da refatoração)

1. Com código **atual** (pré-refatoração), exportar outputs de `VariaveisMercado().get_*()` para `tests/fixtures/variaveis_mercado/`.
2. Rodar cenários de cálculo representativos e salvar golden JSON.
3. Commitar fixtures no repositório.
4. A partir daí, qualquer PR que altere `VariaveisMercado` deve manter os testes verdes ou atualizar fixtures **com justificativa explícita**.

### 6.4 Fonte inicial das fixtures

Prioridade:

1. Arquivos existentes em `titulospub/dados/cache_data/`
2. Backups em `titulospub/dados/backup.py`
3. Parquet do lake (somente na geração de baseline, não no CI)

---

## 7. Infraestrutura de testes

### 7.1 Dependências

Já presentes: `pytest`, `pytest-cov`.

Adicionar se necessário:

- `pyarrow` (leitura parquet na geração de baseline)
- `httpx` (dependência do `TestClient` do FastAPI)

### 7.2 Comandos

```bash
# Suite completa de regressão
pytest tests/ -v

# Apenas contrato VariaveisMercado (rápido)
pytest tests/titulospub/dados/ -v -m regression

# Apenas cálculos
pytest tests/titulospub/core/ -v -m regression

# Apenas API
pytest tests/api/ -v -m regression

# Com cobertura mínima do orquestrador
pytest tests/ --cov=titulospub.dados.orquestrador --cov-report=term-missing
```

### 7.3 Marcadores pytest

Registrar em `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "regression: testes de regressão da refatoração VariaveisMercado",
    "slow: testes que acessam lake/rede (excluídos do CI padrão)",
]
```

### 7.4 CI (recomendado)

Job `regression`:

- Trigger: push/PR em arquivos `titulospub/dados/**`, `titulospub/core/**`, `api/**`
- Comando: `pytest tests/ -m "regression and not slow" -v`
- Sem variáveis de rede/scraping

---

## 8. Padrões de implementação

### 8.1 Stub de teste (`VariaveisMercadoFixture`)

Classe em `tests/conftest.py` que implementa a mesma interface de `VariaveisMercado`, carregando pickles de fixture. Ignora `force_update` (sempre retorna fixture).

### 8.2 Isolamento — código de produção intocado

Os testes devem se adaptar ao código **como está**, sem exigir mudanças:

- Usar `unittest.mock.patch` / `VariaveisMercadoFixture` / injeção via parâmetros **já existentes** (`variaveis_mercado=`).
- Se um ponto não for testável sem alterar produção, usar skip documentado e abrir item para spec futura — **não** alterar produção nesta task.

### 8.3 Referência futura (refatoração — não fazer agora)

Quando existir spec/PR de refatoração (após esta suite estar verde), `VariaveisMercado` deverá:

- Delegar leitura bruta ao pacote/lake
- Normalizar para o **mesmo formato** que o baseline congelou
- Manter fallbacks até decisão explícita de remoção

Isso **não** faz parte da implementação desta spec.

### 8.4 Tolerância numérica

| Tipo              | Tolerância sugerida      |
|-------------------|--------------------------|
| PU, financeiro    | `rel=1e-9` ou `abs=1e-6` |
| Taxas (%)         | `rel=1e-9`               |
| DV01, hedge       | `rel=1e-6`               |
| DataFrames        | `check_exact=False`, `rtol=1e-9` |

### 8.5 Atualização de golden

Só permitida quando:

- Mudança intencional e documentada no PR, **ou**
- Correção de bug comprovada (com referência à spec/issue)

---

## 9. Critérios de aceite

A spec está implementada quando **todos** os itens abaixo forem verdadeiros:

### 9.1 Entregáveis de teste (obrigatório)

- [ ] Existe baseline versionado em `tests/fixtures/variaveis_mercado/`
- [ ] Camada 1 cobre os 6 métodos `get_*` principais
- [ ] Camada 2 cobre LTN, LFT, NTN-B, NTN-F e vencimentos
- [ ] Camada 3 cobre no mínimo 5 endpoints POST da API
- [ ] `pytest tests/ -m regression` passa **sem rede** em < 2 min
- [ ] Documentação de como regenerar baseline existe no README ou nesta spec

### 9.2 Restrição de diff (obrigatório)

- [ ] **Nenhum** arquivo alterado em `titulospub/`, `api/`, `dash_app/` (exceto se o repositório já os tiver modificado por outro motivo — esta task não adiciona diff lá)
- [ ] Diff da PR limitado a `tests/**`, `scripts/` de exportação de fixtures, `specs/**` e config pytest
- [ ] Revisor confirma: PR é **somente testes**, sem refatoração disfarçada

### 9.3 Pronto para a fase seguinte (refatoração — outra task)

- [ ] Suite verde contra código atual
- [ ] Checklist em `tasks.md` das fases 0–5 concluído
- [ ] Spec de refatoração de `VariaveisMercado` pode ser aberta separadamente

---

## 10. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Fixtures desatualizadas vs mercado real | Regenerar baseline periodicamente; testes validam **consistência**, não freshness |
| Testes flaky por data `today()` | Sempre fixar `data_base` nos testes |
| API chama scraping no lifespan | Mock/desabilitar lifespan nos testes |
| Tentação de “só um pequeno fix” no orquestrador | Regra explícita: falha de teste → skip/xfail, não patch em produção |
| Mudança de colunas no lake (futuro) | Testes de contrato falharão na spec de refatoração; adapter em PR separado |
| Golden JSON muito grande | Um cenário enxuto por título; campos essenciais apenas |

---

## 11. Referências no código

| Artefato | Caminho |
|----------|---------|
| Orquestrador | `titulospub/dados/orquestrador.py` |
| Cache | `titulospub/dados/cache.py` |
| Processamento ANBIMA | `titulospub/dados/anbimas.py` |
| Processamento BMF | `titulospub/dados/bmf.py` |
| Vencimentos | `titulospub/dados/vencimentos.py` |
| API lifespan | `api/main.py` |
| Routers | `api/routers/*.py` |
| Dash (HTTP only) | `dash_app/utils/vencimentos.py` |

---

## 12. Histórico

| Versão | Data       | Autor  | Descrição        |
|--------|------------|--------|------------------|
| 0.1    | 2026-05-26 | Rafael | Proposta inicial |
| 0.2    | 2026-05-26 | Rafael | Restrição absoluta: task somente testes, sem alteração de código de produção |
