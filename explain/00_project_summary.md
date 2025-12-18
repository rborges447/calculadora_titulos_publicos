# Resumo Geral do Projeto - Calculadora de Títulos Públicos

## O que é este projeto?

Sistema completo para cálculo e análise de títulos públicos brasileiros. Permite calcular preços, métricas de risco, equivalência entre títulos e gerenciar carteiras através de uma interface web interativa e API REST.

## Problema que resolve

O mercado de títulos públicos brasileiros requer cálculos financeiros complexos e precisos. Este sistema automatiza:

- Cálculos de preços unitários (PU) baseados em taxas de mercado
- Cálculos de métricas de risco (DV01, Duration, Carregamento)
- Cálculos de equivalência entre diferentes títulos
- Gestão de carteiras de múltiplos títulos
- Atualização automática de dados de mercado (ANBIMA, BMF, IPCA)

## Arquitetura em 3 Camadas

### 1. Camada de Domínio (`titulospub/`)
**Responsabilidade:** Lógica de negócio pura (cálculos financeiros)

- Classes de títulos: NTNB, LTN, LFT, NTNF, DI
- Funções de cálculo puras (sem dependências de frameworks web)
- Sistema de equivalência entre títulos
- Classes de carteiras para gestão de múltiplos títulos
- Orquestração de variáveis de mercado
- Scraping e processamento de dados de mercado

**Características:**
- Completamente independente de FastAPI/Dash
- Determinístico (mesmo input → mesmo output)
- Thread-safe (sem estado global mutável por usuário)
- Preparado para escalabilidade

### 2. Camada de API (`api/`)
**Responsabilidade:** Endpoints REST para acesso aos cálculos

- FastAPI com endpoints para cada tipo de título
- Validação de dados via Pydantic
- Gerenciamento de carteiras (estado em memória)
- Endpoints de equivalência e vencimentos

**Características:**
- Stateless (sem estado entre requisições, exceto carteiras)
- Validação automática de dados
- Documentação automática (Swagger/ReDoc)
- Compatível com múltiplos workers (exceto carteiras)

### 3. Camada de Frontend (`dash_app/`)
**Responsabilidade:** Interface web interativa

- Aplicação Dash com páginas para cada tipo de título
- Tabelas editáveis para gestão de carteiras
- Visualização de resultados formatados
- Cálculo de equivalência entre títulos

**Características:**
- Consome exclusivamente a API via HTTP
- Nunca importa `titulospub` diretamente
- Modular e preparado para expansão
- Suporta múltiplos usuários simultâneos

## Tipos de Títulos Suportados

### NTNB (Nota do Tesouro Nacional - Série B)
- **Característica:** Indexado ao IPCA
- **Cupom:** Semestral (6% ao ano)
- **Cálculos:** PU, DV01, Duration, Carregamento, Hedge DAP

### LTN (Letra do Tesouro Nacional)
- **Característica:** Prefixado
- **Cupom:** Zero cupom
- **Cálculos:** PU, DV01, Carregamento, Hedge DI

### LFT (Letra Financeira do Tesouro)
- **Característica:** Pós-fixado (Selic)
- **Cupom:** Zero cupom
- **Cálculos:** PU, Cotação, VNA ajustado

### NTNF (Nota do Tesouro Nacional - Série F)
- **Característica:** Prefixado
- **Cupom:** Semestral
- **Cálculos:** PU, DV01, Carregamento, Hedge DI

### DI (Depósito Interbancário)
- **Característica:** Pós-fixado (CDI)
- **Cupom:** Zero cupom
- **Cálculos:** PU, DV01

## Fluxo de Dados

1. **Inicialização:**
   - API atualiza variáveis de mercado (scraping ou backup)
   - Dados salvos em cache (memória e arquivo)

2. **Requisição de Cálculo:**
   - Cliente envia dados via API
   - API valida dados
   - API cria instância do título (usa dados em cache)
   - API retorna resultados calculados

3. **Interface Web:**
   - Dash faz requisições HTTP para API
   - API processa e retorna dados
   - Dash renderiza resultados formatados

## Dependências Principais

- **Pandas:** Manipulação de dados financeiros
- **FastAPI:** Framework web para API REST
- **Dash:** Framework web para interface interativa
- **Pydantic:** Validação de dados
- **Requests:** Requisições HTTP para scraping

## Pontos de Atenção

1. **Carteiras em memória:** Perdidas se servidor reiniciar
2. **Múltiplos workers:** Carteiras não compartilhadas entre workers
3. **Scraping:** Pode falhar se sites externos estiverem indisponíveis (usa backup)
4. **Cache:** Atualizado automaticamente na inicialização da API (uma vez por dia)

## Próximos Passos Recomendados

1. Migrar carteiras para banco de dados ou Redis (para múltiplos workers)
2. Adicionar sistema de autenticação/autorização
3. Adicionar logging estruturado
4. Adicionar testes automatizados
5. Implementar monitoramento e alertas
