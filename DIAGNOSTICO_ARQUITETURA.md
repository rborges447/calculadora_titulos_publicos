# DIAGNÓSTICO ARQUITETURAL - Calculadora de Títulos Públicos

**Data:** 2024-12-XX  
**Objetivo:** Análise completa da conformidade com a arquitetura oficial do projeto

---

## 1. RESUMO EXECUTIVO

### ✅ Pontos Conformes
- **Separação básica de camadas:** Estrutura de diretórios respeita a divisão titulospub/api/dash_app
- **Dash consumindo API:** Dash não importa titulospub diretamente, usa HTTP via `dash_app/utils/api.py`
- **API usando titulospub:** API importa e usa classes de titulospub corretamente
- **Cálculos isolados:** Lógica de cálculo está em titulospub/core

### ❌ Violações Críticas Encontradas

1. **ESTADO GLOBAL MUTÁVEL NA API** (CRÍTICO)
   - `api/routers/carteiras.py` linha 31: `_carteiras: Dict[str, Dict] = {}`
   - Dicionário global mutável armazena carteiras em memória
   - **Risco:** Não funciona com múltiplos workers, não é thread-safe, dados perdidos entre reinicializações

2. **API COM workers=1 FORÇADO** (CRÍTICO)
   - `run_api.py` linha 15: `workers=1` comentado como necessário para carteiras funcionarem
   - **Risco:** Impossibilita escalabilidade horizontal, gargalo de performance

3. **VariaveisMercado com estado de instância** (MÉDIO)
   - `titulospub/dados/orquestrador.py`: Classe mantém estado em `self._feriados`, `self._ipca_dict`, etc.
   - **Risco:** Se múltiplas instâncias forem criadas, podem ter estados diferentes

4. **Imports não organizados** (BAIXO)
   - Vários arquivos não seguem padrão: padrão → terceiros → internos

5. **README desatualizado** (BAIXO)
   - Menciona Streamlit, mas projeto usa Dash

---

## 2. ANÁLISE DETALHADA POR CAMADA

### 2.1 CAMADA DE DOMÍNIO (`titulospub/`)

#### ✅ Conformidades
- **Independência:** Não importa FastAPI, Dash ou frameworks web
- **Lógica isolada:** Cálculos estão em `core/`
- **Determinístico:** Funções de cálculo são puras (mesmo input → mesmo output)

#### ⚠️ Pontos de Atenção
- **VariaveisMercado:** Classe com estado de instância (`self._feriados`, etc.)
  - **Impacto:** Se múltiplas instâncias forem criadas, podem ter estados dessincronizados
  - **Solução:** Considerar padrão singleton thread-safe ou cache compartilhado (Redis/file system)
  - **Prioridade:** MÉDIA (funciona, mas pode causar problemas em escala)

- **Cache em arquivo:** `titulospub/dados/cache.py` usa sistema de arquivos
  - **Impacto:** Funciona, mas pode ser lento com muitos workers
  - **Solução:** Manter (é adequado para cache imutável)

#### ❌ Violações
- **Nenhuma violação crítica encontrada**

---

### 2.2 CAMADA DE API (`api/`)

#### ✅ Conformidades
- **Usa titulospub:** Importa e chama classes/funções de titulospub corretamente
- **Stateless endpoints:** Endpoints individuais (ltn, ntnb, etc.) são stateless
- **Validação:** Usa Pydantic para validação de entrada

#### ❌ Violações Críticas

**1. Estado Global Mutável - Carteiras (`api/routers/carteiras.py`)**
```python
# Linha 31
_carteiras: Dict[str, Dict] = {}
```
- **Problema:** Dicionário global mutável armazena carteiras em memória
- **Impacto:**
  - ❌ Não funciona com múltiplos workers (cada worker tem sua própria memória)
  - ❌ Não é thread-safe (race conditions em atualizações)
  - ❌ Dados perdidos ao reiniciar servidor
  - ❌ Não escala para múltiplos usuários simultâneos
- **Evidência:** `run_api.py` linha 15 comenta: `workers=1` necessário para carteiras funcionarem
- **Solução necessária:** Migrar para banco de dados ou cache compartilhado (Redis)

**2. Lifespan com atualização de mercado (`api/main.py`)**
- **Problema:** Atualiza variáveis de mercado no startup da API
- **Impacto:** Pode causar lentidão no startup, mas é aceitável se feito uma vez por dia
- **Solução:** Manter, mas considerar fazer em processo separado (cron job)

#### ⚠️ Pontos de Atenção
- **Imports:** Alguns arquivos não seguem ordem padrão → terceiros → internos
- **Tratamento de erros:** Alguns endpoints retornam 500 genérico, deveriam ser mais específicos

---

### 2.3 CAMADA DE FRONTEND (`dash_app/`)

#### ✅ Conformidades
- **Não importa titulospub:** Verificado via grep - nenhum import direto encontrado
- **Consome API via HTTP:** Usa `dash_app/utils/api.py` e `dash_app/utils/carteiras.py` que fazem requests HTTP
- **Modular:** Estrutura de páginas e componentes está organizada

#### ⚠️ Pontos de Atenção
- **Estado no cliente:** Dash mantém estado no navegador (via `dcc.Store`), o que é correto
- **Tratamento de erros:** Alguns callbacks poderiam ter melhor tratamento de erros

#### ❌ Violações
- **Nenhuma violação crítica encontrada**

---

### 2.4 SCRIPTS DE DEPLOY

#### ✅ Conformidades
- **run_api.py:** Usa uvicorn corretamente
- **run_dash_app.py:** Usa app.run() (aceitável para desenvolvimento)

#### ❌ Violações

**1. run_api.py - workers=1 forçado**
```python
# Linha 15
workers=1,  # Usar 1 worker para carteiras em memória funcionarem corretamente
```
- **Problema:** Comentário explicita que múltiplos workers não funcionam
- **Causa raiz:** Estado global `_carteiras` em `api/routers/carteiras.py`
- **Impacto:** Impossibilita escalabilidade horizontal

**2. run_dash_app.py - debug=True**
```python
# Linha 8
app.run(debug=True, port=8050, host="127.0.0.1")
```
- **Problema:** `debug=True` não deve ser usado em produção
- **Impacto:** Baixo (script de desenvolvimento), mas deveria ter flag de ambiente

---

## 3. RISCOS DE CONCORRÊNCIA E ESCALABILIDADE

### 🔴 Riscos Críticos

1. **Estado Global `_carteiras`**
   - **Cenário:** 2 usuários criam carteiras simultaneamente
   - **Risco:** Race condition ao escrever no dicionário (baixo risco em Python devido ao GIL, mas existe)
   - **Cenário:** API com 2 workers, usuário cria carteira no worker 1, tenta acessar no worker 2
   - **Risco:** Carteira não encontrada (dados em memória do worker 1)
   - **Impacto:** ALTO - Sistema não funciona corretamente com múltiplos workers

2. **VariaveisMercado - múltiplas instâncias**
   - **Cenário:** Cada worker cria sua própria instância de VariaveisMercado
   - **Risco:** Estados dessincronizados entre workers
   - **Impacto:** MÉDIO - Pode causar inconsistências em cálculos

### 🟡 Riscos Médios

1. **Cache em arquivo compartilhado**
   - **Cenário:** Múltiplos workers tentam escrever cache simultaneamente
   - **Risco:** Race condition ao escrever arquivo
   - **Impacto:** BAIXO - Cache é principalmente leitura, escrita rara

---

## 4. DEPENDÊNCIAS ENTRE CAMADAS

### ✅ Dependências Corretas
```
titulospub/  (independente)
    ↑
    | importa
    |
api/  (importa titulospub)
    ↑
    | HTTP requests
    |
dash_app/  (consome API via HTTP)
```

### ❌ Dependências Indevidas
- **Nenhuma encontrada** - Dash não importa titulospub diretamente ✅

---

## 5. PONTOS FRÁGEIS PARA PRODUTO COM CLIENTES

### 🔴 Críticos

1. **Escalabilidade horizontal impossibilitada**
   - Estado global `_carteiras` impede uso de múltiplos workers
   - **Impacto:** Não pode escalar horizontalmente para suportar 100+ usuários simultâneos
   - **Solução:** Migrar carteiras para banco de dados ou Redis

2. **Perda de dados ao reiniciar**
   - Carteiras são perdidas ao reiniciar servidor
   - **Impacto:** Experiência ruim para usuários
   - **Solução:** Persistência em banco de dados

### 🟡 Médios

1. **Falta de testes automatizados**
   - Não há suíte de testes estruturada
   - **Impacto:** Risco de regressões ao fazer mudanças
   - **Solução:** Criar testes (TAREFA 2)

2. **Tratamento de erros genérico**
   - Alguns endpoints retornam 500 genérico
   - **Impacto:** Debugging difícil em produção
   - **Solução:** Melhorar tratamento de erros

### 🟢 Baixos

1. **README desatualizado**
   - Menciona Streamlit em vez de Dash
   - **Impacto:** Confusão para novos desenvolvedores
   - **Solução:** Atualizar README

2. **Imports não organizados**
   - Não segue padrão padrão → terceiros → internos
   - **Impacto:** Legibilidade reduzida
   - **Solução:** Organizar imports (TAREFA 3)

---

## 6. PLANO INCREMENTAL DE MUDANÇAS

### FASE 1: Testes (TAREFA 2) ⚠️ CRÍTICO ANTES DE REFATORAR
**Objetivo:** Congelar comportamento atual antes de qualquer mudança

1. Criar `tests/` estruturado com pytest
2. Testes de cálculos principais (`titulospub/core`)
3. Testes de API (TestClient do FastAPI)
4. Smoke test do Dash (inicialização + rota principal)
5. Testes de múltiplas chamadas para garantir ausência de estado global

**Critério de sucesso:** Todos os testes passam e "congelam" comportamento atual

---

### FASE 2: Limpeza (TAREFA 3) 🟢 BAIXO RISCO
**Objetivo:** Melhorar legibilidade sem alterar comportamento

1. Remover imports não utilizados (com cautela)
2. Organizar imports: padrão → terceiros → internos
3. Melhorar formatação e legibilidade

**Critério de sucesso:** Testes continuam passando, código mais limpo

---

### FASE 3: Separação de Camadas (TAREFA 4) 🟡 MÉDIO RISCO
**Objetivo:** Garantir que arquitetura seja respeitada

1. Verificar que Dash não importa titulospub (já está OK ✅)
2. Verificar que API não executa cálculos (já está OK ✅)
3. Verificar que titulospub não importa API/Dash (já está OK ✅)
4. **NOVO:** Remover estado global mutável de carteiras
   - Opção A: Migrar para banco de dados (PostgreSQL/SQLite)
   - Opção B: Usar Redis como cache compartilhado
   - Opção C: Tornar carteiras stateless (retornar dados completos, sem armazenar)

**Critério de sucesso:** API funciona com `workers > 1`, testes passam

---

### FASE 4: Consolidação (TAREFA 5) 🟢 BAIXO RISCO
**Objetivo:** Verificar que tudo funciona e documentar melhorias

1. Rodar todos os testes
2. Verificar que comportamento não mudou (mesmos inputs → mesmos outputs)
3. Documentar melhorias aplicadas
4. Atualizar README

**Critério de sucesso:** Sistema funciona igual ao inicial, mas com arquitetura correta

---

## 7. DECISÕES ARQUITETURAIS NECESSÁRIAS

### Decisão 1: Persistência de Carteiras
**Opções:**
- **A) Banco de dados (PostgreSQL/SQLite)**
  - ✅ Persistência permanente
  - ✅ Funciona com múltiplos workers
  - ✅ Thread-safe
  - ❌ Requer setup de banco de dados
  - ❌ Mais complexo

- **B) Redis**
  - ✅ Cache compartilhado entre workers
  - ✅ Thread-safe
  - ✅ Rápido
  - ❌ Requer Redis instalado
  - ❌ Dados podem ser perdidos se Redis reiniciar

- **C) Stateless (sem armazenamento)**
  - ✅ Mais simples
  - ✅ Sempre funciona
  - ❌ Cliente precisa enviar dados completos a cada requisição
  - ❌ Pode ser mais lento para carteiras grandes

**Recomendação:** Opção C (stateless) para MVP, migrar para A ou B quando necessário

---

### Decisão 2: VariaveisMercado
**Situação atual:** Classe com estado de instância
**Opções:**
- **A) Singleton thread-safe**
  - ✅ Uma única instância compartilhada
  - ❌ Pode causar problemas com múltiplos workers

- **B) Cache compartilhado (arquivo/Redis)**
  - ✅ Funciona com múltiplos workers
  - ✅ Estado consistente
  - ✅ Já implementado parcialmente (cache em arquivo)

**Recomendação:** Manter como está (cache em arquivo funciona bem para dados imutáveis)

---

## 8. CHECKLIST DE CONFORMIDADE

### Arquitetura Oficial
- [x] titulospub/ independente de frameworks web
- [x] API importa titulospub (correto)
- [x] Dash não importa titulospub (correto)
- [x] Dash consome API via HTTP (correto)
- [ ] API stateless (❌ violado por `_carteiras`)
- [ ] Compatível com múltiplos workers (❌ violado por `_carteiras`)

### Escalabilidade
- [ ] Thread-safe (❌ `_carteiras` não é thread-safe)
- [ ] Sem estado global mutável por usuário (❌ `_carteiras` é estado global)
- [ ] Funciona com múltiplos workers (❌ `workers=1` forçado)
- [x] Cálculos determinísticos (correto)

### Qualidade
- [ ] Imports organizados (⚠️ parcial)
- [ ] Sem imports não utilizados (⚠️ precisa verificar)
- [ ] Testes automatizados (❌ não existe)
- [ ] README atualizado (❌ menciona Streamlit)

---

## 9. CONCLUSÃO

### Status Geral: ⚠️ PARCIALMENTE CONFORME

**Pontos Fortes:**
- Separação básica de camadas está correta
- Dash não viola arquitetura (consome API via HTTP)
- Cálculos são determinísticos e isolados

**Pontos Críticos a Corrigir:**
1. **Estado global `_carteiras`** - impede escalabilidade horizontal
2. **Falta de testes** - risco de regressões
3. **workers=1 forçado** - limitação de escalabilidade

**Próximos Passos:**
1. Criar suíte de testes (TAREFA 2) - CRÍTICO antes de refatorar
2. Limpar código (TAREFA 3) - baixo risco
3. Remover estado global (TAREFA 4) - médio risco, requer decisão arquitetural
4. Consolidar e documentar (TAREFA 5)

---

**Documento gerado em:** 2024-12-XX  
**Próxima revisão:** Após implementação das TAREFAS 2-5
