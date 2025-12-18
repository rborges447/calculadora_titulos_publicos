# Documentação Completa do Codebase - Calculadora de Títulos Públicos

## 1. VISÃO GERAL DO PROJETO

### O que o projeto faz

Este projeto é um sistema completo para cálculo e análise de títulos públicos brasileiros. Ele permite:

- **Cálculo de preços unitários (PU)** de diferentes tipos de títulos (LTN, LFT, NTNB, NTNF, DI)
- **Cálculo de métricas de risco** (DV01, Duration, Carregamento)
- **Cálculo de equivalência** entre diferentes títulos
- **Gestão de carteiras** de títulos públicos
- **Interface web interativa** para visualização e edição de cálculos
- **API REST** para integração com outros sistemas

### Problema que resolve

O mercado de títulos públicos brasileiros requer cálculos financeiros complexos e precisos. Este sistema automatiza:

- Cálculos de preços baseados em taxas de mercado
- Ajustes de liquidação e carregamento
- Cálculos de hedge (DI e DAP)
- Equivalência entre títulos para comparação de posições
- Atualização automática de dados de mercado (ANBIMA, BMF, IPCA)

### Principais subsistemas

1. **Camada de Domínio (`titulospub/`)**
   - Lógica de negócio pura (cálculos financeiros)
   - Classes de títulos (NTNB, LTN, LFT, NTNF, DI)
   - Funções de cálculo auxiliares
   - Sistema de equivalência

2. **Camada de Dados (`titulospub/dados/`)**
   - Orquestração de variáveis de mercado
   - Sistema de cache
   - Processamento de dados ANBIMA, BMF, IPCA
   - Funções de backup

3. **Camada de Scraping (`titulospub/scraping/`)**
   - Coleta de dados de fontes externas
   - Scraping de sites ANBIMA, BMF, SIDRA
   - Processamento e normalização de dados

4. **Camada de API (`api/`)**
   - Endpoints REST para cada tipo de título
   - Validação de dados via Pydantic
   - Gerenciamento de carteiras

5. **Camada de Frontend (`dash_app/`)**
   - Interface web interativa
   - Tabelas editáveis para cada tipo de título
   - Visualização de resultados

### Separação conceitual

- **Cálculo**: Toda lógica financeira está em `titulospub/core/` e é completamente independente de frameworks web
- **Infraestrutura**: API e Dash são apenas camadas de apresentação que consomem a lógica de cálculo
- **Interface**: O Dash consome exclusivamente a API via HTTP, nunca importa `titulospub` diretamente

---

## 2. ÁRVORE DO PROJETO COMENTADA

```
calculadora_titulos_publicos/
│
├── titulospub/                    # Camada de Domínio - Lógica de negócio pura
│   ├── __init__.py                # Exporta classes e funções principais do módulo
│   │
│   ├── core/                      # Classes e cálculos principais dos títulos
│   │   ├── __init__.py            # Exporta classes NTNB, LTN, LFT, NTNF, DI
│   │   ├── auxilio.py             # Funções auxiliares (códigos BMF, PU carregado)
│   │   ├── equivalencia.py        # Função de equivalência entre títulos
│   │   │
│   │   ├── carteiras/             # Classes para gestão de carteiras
│   │   │   ├── __init__.py        # Exporta classes de carteiras
│   │   │   ├── carteira_lft.py    # Carteira de títulos LFT
│   │   │   ├── carteira_ltn.py    # Carteira de títulos LTN
│   │   │   ├── carteira_ntnb.py   # Carteira de títulos NTNB
│   │   │   └── carteira_ntnf.py   # Carteira de títulos NTNF
│   │   │
│   │   ├── dap/                   # Cálculos relacionados a DAP (Dívida Ativa Pública)
│   │   │   └── calculo_dap.py     # Funções de cálculo de PU, DV01 e financeiro DAP
│   │   │
│   │   ├── di/                    # Cálculos relacionados a DI (Depósito Interbancário)
│   │   │   ├── calculo_di.py      # Funções de cálculo de taxa/PU e DV01 DI
│   │   │   └── di_contrato.py    # Classe DI para representar contratos DI
│   │   │
│   │   ├── lft/                   # Cálculos específicos de LFT
│   │   │   ├── ajuste_vna_lft.py # Cálculo de VNA ajustado para LFT
│   │   │   ├── calculo_lft.py    # Funções de cálculo de PU e taxa LFT
│   │   │   └── titulo_lft.py     # Classe LFT (Letra Financeira do Tesouro)
│   │   │
│   │   ├── ltn/                   # Cálculos específicos de LTN
│   │   │   ├── calculo_ltn.py    # Funções de cálculo de PU, taxa, DV01 LTN
│   │   │   └── titulo_ltn.py     # Classe LTN (Letra do Tesouro Nacional)
│   │   │
│   │   ├── ntnb/                  # Cálculos específicos de NTNB
│   │   │   ├── calculo_ntnb.py   # Funções de cálculo de PU, taxa, DV01, duration NTNB
│   │   │   ├── cash_flow_ntnb.py  # Cálculo de fluxo de caixa (cupons) NTNB
│   │   │   ├── titulo_ntnb.py    # Classe NTNB (Nota do Tesouro Nacional - Série B)
│   │   │   └── vna_ntnb.py       # Cálculo de VNA (Valor Nominal Ajustado) NTNB
│   │   │
│   │   ├── ntnf/                  # Cálculos específicos de NTNF
│   │   │   ├── calculo_ntnf.py   # Funções de cálculo de PU, taxa, DV01 NTNF
│   │   │   ├── cash_flow_ntnf.py # Cálculo de fluxo de caixa (cupons) NTNF
│   │   │   └── titulo_ntnf.py    # Classe NTNF (Nota do Tesouro Nacional - Série F)
│   │   │
│   │   └── interpolacao/         # Funções de interpolação (se houver)
│   │       └── funcoes_interpolacao.py
│   │
│   ├── dados/                     # Camada de dados e orquestração
│   │   ├── __init__.py            # Exporta funções de backup, cache, VariaveisMercado
│   │   ├── anbimas.py             # Processamento de dados ANBIMA
│   │   ├── backup.py              # Funções de backup (fallback quando scraping falha)
│   │   ├── bmf.py                 # Processamento de dados BMF (ajustes DI e DAP)
│   │   ├── cache.py               # Sistema de cache (save/load/clear)
│   │   ├── ipca.py                # Processamento de dados IPCA
│   │   ├── orquestrador.py        # Classe VariaveisMercado (orquestra todas variáveis)
│   │   ├── vencimentos.py         # Funções para obter vencimentos disponíveis
│   │   │
│   │   └── backup_excel/          # Arquivos Excel de backup (fallback)
│   │       ├── anbimas.xlsx
│   │       ├── bmf.xlsx
│   │       ├── cdi.xlsx
│   │       ├── feriados.xlsx
│   │       ├── ipca_fechado.xlsx
│   │       └── ipca_proj.xlsx
│   │
│   ├── scraping/                  # Coleta de dados de fontes externas
│   │   ├── __init__.py            # Exporta funções de scraping
│   │   ├── anbima_scraping.py     # Scraping de dados ANBIMA (taxas, CDI, feriados, IPCA proj)
│   │   ├── bmf_net_scraping.py    # Scraping de dados BMF Net
│   │   ├── sidra_scraping.py      # Scraping de dados IPCA fechado via SIDRA
│   │   └── uptodata_scraping.py   # Scraping de ajustes BMF via UpToData
│   │
│   └── utils/                     # Utilitários gerais
│       ├── __init__.py            # Exporta funções utilitárias
│       ├── carregamento_var_globais.py # Funções de carregamento condicional de variáveis
│       ├── datas.py               # Funções de manipulação de datas (dias úteis, feriados)
│       └── paths.py               # Funções para caminhos de arquivos (backup, cache, logs)
│
├── api/                           # Camada de API REST (FastAPI)
│   ├── __init__.py                # Módulo vazio
│   ├── main.py                    # Aplicação FastAPI principal (cria app, registra routers)
│   ├── models.py                  # Modelos Pydantic (Request/Response)
│   ├── utils.py                   # Utilitários da API (serialização, controle atualização)
│   │
│   └── routers/                   # Endpoints organizados por funcionalidade
│       ├── __init__.py            # Módulo vazio
│       ├── carteiras.py            # Endpoints de carteiras (criar, obter, atualizar)
│       ├── equivalencia.py         # Endpoint de equivalência entre títulos
│       ├── lft.py                  # Endpoints de título LFT
│       ├── ltn.py                  # Endpoints de título LTN
│       ├── ntnb.py                 # Endpoints de título NTNB
│       ├── ntnf.py                 # Endpoints de título NTNF
│       └── vencimentos.py          # Endpoints de vencimentos disponíveis
│
├── dash_app/                      # Camada de Frontend (Dash)
│   ├── __init__.py                # Módulo vazio
│   ├── app.py                     # Aplicação Dash principal (layout, routing)
│   ├── config.py                  # Configurações globais (API_URL, título, rotas)
│   │
│   ├── components/                # Componentes reutilizáveis
│   │   ├── __init__.py            # Módulo vazio
│   │   └── navbar.py              # Componente de navegação (navbar)
│   │
│   ├── pages/                     # Páginas da aplicação
│   │   ├── __init__.py            # Módulo vazio
│   │   ├── home.py                # Página inicial
│   │   ├── lft.py                 # Página de cálculos LFT
│   │   ├── ltn.py                 # Página de cálculos LTN
│   │   ├── ntnb.py                # Página de cálculos NTNB
│   │   ├── ntnb_hedge.py          # Página de hedge DI para NTNB
│   │   └── ntnf.py                # Página de cálculos NTNF
│   │
│   └── utils/                     # Utilitários do frontend
│       ├── __init__.py            # Módulo vazio
│       ├── api.py                 # Funções de chamada HTTP à API
│       ├── carteiras.py           # Funções de manipulação de carteiras
│       ├── formatacao.py          # Funções de formatação de números (taxas, PU, etc)
│       └── vencimentos.py         # Funções de formatação de vencimentos
│
├── run_api.py                     # Script para iniciar API FastAPI (uvicorn)
├── run_dash_app.py               # Script para iniciar aplicação Dash
│
├── setup.py                       # Configuração do pacote Python
├── pyproject.toml                 # Metadados do projeto (poetry/pip)
├── MANIFEST.in                    # Arquivos a incluir no pacote
├── requirements.txt               # Dependências do projeto
├── README.md                      # Documentação básica do projeto
├── RUNBOOK.md                     # Guia de execução em rede interna
└── .gitignore                     # Arquivos ignorados pelo Git
```

---

## 3. MAPA DE DEPENDÊNCIAS

### Quem importa quem

#### Camada de Domínio (`titulospub/`)

**Núcleo independente:**
- `titulospub/core/` → Não importa nada externo (apenas pandas, numpy, bibliotecas padrão)
- `titulospub/utils/` → Não importa nada de outras camadas do projeto

**Dependências internas:**
- `titulospub/core/*/titulo_*.py` → Importa de `titulospub/core/*/calculo_*.py`
- `titulospub/core/*/titulo_*.py` → Importa de `titulospub/dados/orquestrador.py`
- `titulospub/core/equivalencia.py` → Importa classes de títulos de `titulospub/core/`

**Camada de dados:**
- `titulospub/dados/orquestrador.py` → Importa de `titulospub/scraping/` e `titulospub/dados/backup.py`
- `titulospub/dados/anbimas.py` → Importa de `titulospub/dados/backup.py` (fallback)
- `titulospub/dados/bmf.py` → Importa de `titulospub/dados/backup.py` (fallback)
- `titulospub/dados/ipca.py` → Importa de `titulospub/dados/backup.py` (fallback)

**Camada de scraping:**
- `titulospub/scraping/*` → Não importa nada do projeto (apenas bibliotecas externas)

#### Camada de API (`api/`)

- `api/main.py` → Importa de `titulospub/dados/orquestrador.py` e `api/routers/*`
- `api/routers/*` → Importam de `titulospub/core/*` (classes de títulos)
- `api/models.py` → Não importa nada do projeto (apenas Pydantic)
- `api/utils.py` → Não importa nada do projeto (apenas bibliotecas padrão)

#### Camada de Frontend (`dash_app/`)

- `dash_app/app.py` → Importa apenas de `dash_app/` (nunca importa `titulospub`)
- `dash_app/pages/*` → Importam de `dash_app/utils/api.py` (chamadas HTTP)
- `dash_app/utils/api.py` → Faz requisições HTTP para a API (não importa `titulospub`)

### Módulos núcleo (sem dependências do projeto)

1. `titulospub/core/*/calculo_*.py` - Funções puras de cálculo
2. `titulospub/utils/datas.py` - Funções de datas
3. `titulospub/utils/paths.py` - Funções de caminhos
4. `titulospub/scraping/*` - Funções de scraping

### Módulos com side effects (IO, rede, arquivos)

1. **IO de arquivos:**
   - `titulospub/dados/cache.py` - Leitura/escrita de arquivos pickle
   - `titulospub/dados/backup.py` - Leitura de arquivos Excel
   - `titulospub/utils/paths.py` - Construção de caminhos de arquivos

2. **Rede/HTTP:**
   - `titulospub/scraping/anbima_scraping.py` - Requisições HTTP para ANBIMA
   - `titulospub/scraping/sidra_scraping.py` - Requisições HTTP para SIDRA
   - `titulospub/scraping/bmf_net_scraping.py` - Requisições HTTP para BMF
   - `titulospub/scraping/uptodata_scraping.py` - Requisições HTTP para UpToData
   - `dash_app/utils/api.py` - Requisições HTTP para API FastAPI

3. **Estado global:**
   - `titulospub/dados/orquestrador.py` - Mantém cache em memória (`_feriados`, `_ipca_dict`, etc)
   - `api/routers/carteiras.py` - Mantém carteiras em memória (dicionário global)

---

## 4. DOCUMENTAÇÃO POR MÓDULO

### `titulospub/__init__.py`

**Responsabilidade:** Ponto de entrada principal do módulo `titulospub`. Exporta todas as classes e funções públicas.

**O que faz:**
- Importa e re-exporta classes de títulos (NTNB, LTN, LFT, NTNF, DI)
- Importa e re-exporta função de equivalência
- Importa e re-exporta funções de scraping
- Importa e re-exporta funções utilitárias
- Importa e re-exporta funções de dados
- Define `__all__` com lista de exports públicos
- Fornece funções auxiliares (`get_info_modulos()`, `listar_funcionalidades()`, `criar_titulo()`)

**O que NÃO faz:**
- Não contém lógica de cálculo
- Não faz scraping diretamente
- Não mantém estado

**Dependências relevantes:**
- Importa de `titulospub.core`, `titulospub.scraping`, `titulospub.utils`, `titulospub.dados`

**Side effects:** Nenhum

---

### `titulospub/core/__init__.py`

**Responsabilidade:** Exporta todas as classes de títulos e funções de cálculo do módulo core.

**O que faz:**
- Importa classes de títulos de seus respectivos módulos
- Importa funções de cálculo de DI e DAP
- Importa função de equivalência
- Define `__all__` com lista de exports
- Adiciona docstrings às classes exportadas
- Fornece funções auxiliares (`get_titulos_disponiveis()`, `criar_titulo()`, `listar_titulos()`)

**O que NÃO faz:**
- Não contém implementação de cálculos
- Não mantém estado

**Dependências relevantes:**
- Importa de `titulospub.core.ntnb.titulo_ntnb`, `titulospub.core.ltn.titulo_ltn`, etc.

**Side effects:** Nenhum

---

### `titulospub/core/ntnb/titulo_ntnb.py`

**Responsabilidade:** Classe principal para cálculo e gestão de títulos NTN-B.

**O que faz:**
- Representa um título NTN-B com todos seus atributos
- Calcula preço unitário (PU) à vista e a termo
- Calcula DV01 (sensibilidade à mudança de taxa)
- Calcula carregamento (diferença entre PU carregado e ajustado)
- Calcula hedge DAP (quantidade de contratos DAP para hedge)
- Calcula duration e data de vencimento da duration
- Permite definir posição por quantidade ou valor financeiro
- Busca taxa ANBIMA automaticamente se não fornecida
- Calcula VNA ajustado baseado em IPCA

**O que NÃO faz:**
- Não faz scraping diretamente (usa VariaveisMercado)
- Não persiste dados
- Não gerencia múltiplos títulos (use CarteiraNTNB)

**Dependências relevantes:**
- `titulospub.core.ntnb.calculo_ntnb` - Funções de cálculo
- `titulospub.core.ntnb.vna_ntnb` - Cálculo de VNA
- `titulospub.core.ntnb.cash_flow_ntnb` - Fluxo de cupons
- `titulospub.core.dap.calculo_dap` - Cálculos DAP
- `titulospub.dados.orquestrador` - Variáveis de mercado

**Side effects:**
- Lê dados de mercado via VariaveisMercado (pode fazer scraping se necessário)

**Principais métodos:**
- `__init__()` - Inicializa título com parâmetros
- `@property quantidade` - Getter/setter de quantidade
- `@property financeiro` - Getter/setter de valor financeiro
- `@property pu_d0` - Preço unitário à vista
- `@property pu_termo` - Preço unitário a termo
- `@property dv01` - DV01 do título
- `@property carrego_brl` - Carregamento em reais
- `_calcular()` - Executa todos os cálculos

---

### `titulospub/core/ltn/titulo_ltn.py`

**Responsabilidade:** Classe principal para cálculo e gestão de títulos LTN.

**O que faz:**
- Representa um título LTN com todos seus atributos
- Calcula preço unitário (PU) à vista e a termo
- Calcula DV01
- Calcula carregamento
- Calcula hedge DI (quantidade de contratos DI para hedge)
- Permite definir posição por quantidade ou valor financeiro
- Busca taxa ANBIMA automaticamente se não fornecida
- Calcula taxa a partir de prêmio sobre DI se fornecido

**O que NÃO faz:**
- Não faz scraping diretamente
- Não persiste dados
- Não gerencia múltiplos títulos

**Dependências relevantes:**
- `titulospub.core.ltn.calculo_ltn` - Funções de cálculo
- `titulospub.core.di.calculo_di` - Cálculos DI
- `titulospub.dados.orquestrador` - Variáveis de mercado

**Side effects:**
- Lê dados de mercado via VariaveisMercado

---

### `titulospub/core/lft/titulo_lft.py`

**Responsabilidade:** Classe principal para cálculo e gestão de títulos LFT.

**O que faz:**
- Representa um título LFT com todos seus atributos
- Calcula preço unitário (PU) baseado em VNA ajustado
- Calcula cotação
- Permite definir posição por quantidade ou valor financeiro
- Busca taxa ANBIMA automaticamente se não fornecida
- Calcula VNA ajustado baseado em CDI e VNA LFT

**O que NÃO faz:**
- Não calcula DV01 (LFT não tem sensibilidade a taxa prefixada)
- Não faz scraping diretamente
- Não persiste dados

**Dependências relevantes:**
- `titulospub.core.lft.calculo_lft` - Funções de cálculo
- `titulospub.core.lft.ajuste_vna_lft` - Ajuste de VNA
- `titulospub.dados.orquestrador` - Variáveis de mercado

**Side effects:**
- Lê dados de mercado via VariaveisMercado

---

### `titulospub/core/ntnf/titulo_ntnf.py`

**Responsabilidade:** Classe principal para cálculo e gestão de títulos NTN-F.

**O que faz:**
- Representa um título NTN-F com todos seus atributos
- Calcula preço unitário (PU) à vista e a termo
- Calcula DV01
- Calcula carregamento
- Calcula hedge DI
- Permite definir posição por quantidade ou valor financeiro
- Busca taxa ANBIMA automaticamente se não fornecida
- Calcula taxa a partir de prêmio sobre DI se fornecido

**O que NÃO faz:**
- Não faz scraping diretamente
- Não persiste dados
- Não gerencia múltiplos títulos

**Dependências relevantes:**
- `titulospub.core.ntnf.calculo_ntnf` - Funções de cálculo
- `titulospub.core.di.calculo_di` - Cálculos DI
- `titulospub.dados.orquestrador` - Variáveis de mercado

**Side effects:**
- Lê dados de mercado via VariaveisMercado

---

### `titulospub/core/di/di_contrato.py`

**Responsabilidade:** Classe para representar contratos DI (Depósito Interbancário).

**O que faz:**
- Representa um contrato DI com código e taxa
- Calcula preço unitário (PU)
- Calcula DV01
- Permite definir posição por quantidade ou valor financeiro
- Valida código DI

**O que NÃO faz:**
- Não faz scraping diretamente
- Não persiste dados

**Dependências relevantes:**
- `titulospub.core.di.calculo_di` - Funções de cálculo
- `titulospub.core.auxilio` - Funções auxiliares

**Side effects:** Nenhum

---

### `titulospub/core/equivalencia.py`

**Responsabilidade:** Calcular equivalência entre dois títulos diferentes.

**O que faz:**
- Calcula quantidade equivalente de um título baseado em outro
- Suporta critérios: 'dv' (DV01) ou 'fin' (financeiro)
- Cria instâncias temporárias dos títulos para cálculo
- Retorna quantidade equivalente do segundo título

**O que NÃO faz:**
- Não modifica os títulos originais
- Não persiste resultados

**Dependências relevantes:**
- Importa classes de títulos de `titulospub.core`

**Side effects:**
- Cria instâncias temporárias de títulos (pode fazer scraping via VariaveisMercado)

---

### `titulospub/core/carteiras/carteira_ntnb.py`

**Responsabilidade:** Gerenciar carteira de múltiplos títulos NTN-B.

**O que faz:**
- Armazena múltiplos títulos NTN-B
- Permite adicionar/remover títulos
- Calcula totais da carteira (quantidade, financeiro, DV01)
- Permite atualizar taxa de um título específico
- Permite atualizar dias de liquidação globalmente
- Retorna dados formatados para API

**O que NÃO faz:**
- Não persiste dados (estado em memória)
- Não faz scraping diretamente

**Dependências relevantes:**
- `titulospub.core.ntnb.titulo_ntnb` - Classe NTNB

**Side effects:**
- Mantém estado em memória (dicionário de títulos)

---

### `titulospub/core/carteiras/carteira_ltn.py`

**Responsabilidade:** Gerenciar carteira de múltiplos títulos LTN.

**O que faz:**
- Similar a CarteiraNTNB, mas para LTN
- Suporta atualização de prêmio e DI (além de taxa)

**Dependências relevantes:**
- `titulospub.core.ltn.titulo_ltn` - Classe LTN

**Side effects:**
- Mantém estado em memória

---

### `titulospub/core/carteiras/carteira_lft.py`

**Responsabilidade:** Gerenciar carteira de múltiplos títulos LFT.

**O que faz:**
- Similar a outras carteiras, mas para LFT

**Dependências relevantes:**
- `titulospub.core.lft.titulo_lft` - Classe LFT

**Side effects:**
- Mantém estado em memória

---

### `titulospub/core/carteiras/carteira_ntnf.py`

**Responsabilidade:** Gerenciar carteira de múltiplos títulos NTN-F.

**O que faz:**
- Similar a outras carteiras, mas para NTNF
- Suporta atualização de prêmio e DI

**Dependências relevantes:**
- `titulospub.core.ntnf.titulo_ntnf` - Classe NTNF

**Side effects:**
- Mantém estado em memória

---

### `titulospub/core/ntnb/calculo_ntnb.py`

**Responsabilidade:** Funções puras de cálculo para NTN-B.

**O que faz:**
- `calculo_duration()` - Calcula duration de Macaulay
- `data_vencimento_duration()` - Calcula data de vencimento da duration
- `calculo_dv01_ntnb()` - Calcula DV01 do título
- `cauculo_pu_carregado()` - Calcula PU carregado (com juros)
- `calculo_pu_ajustado()` - Calcula PU ajustado (com IPCA)
- `calculo_carrego_ntnb()` - Calcula carregamento
- `calculo_taxa_pu_ntnb()` - Calcula taxa a partir de PU
- `calculo_ntnb()` - Função principal que calcula todos os valores

**O que NÃO faz:**
- Não mantém estado
- Não faz IO
- Não faz scraping

**Dependências relevantes:**
- `titulospub.core.ntnb.cash_flow_ntnb` - Para fluxo de cupons
- `titulospub.utils.datas` - Para manipulação de datas

**Side effects:** Nenhum

---

### `titulospub/core/ltn/calculo_ltn.py`

**Responsabilidade:** Funções puras de cálculo para LTN.

**O que faz:**
- `taxa_pu_ltn()` - Calcula PU a partir de taxa
- `pu_taxa_ltn()` - Calcula taxa a partir de PU
- `calculo_dv01_ltn()` - Calcula DV01
- `calculo_carrego_ltn()` - Calcula carregamento
- `calcular_ltn()` - Função principal

**Side effects:** Nenhum

---

### `titulospub/core/lft/calculo_lft.py`

**Responsabilidade:** Funções puras de cálculo para LFT.

**O que faz:**
- `pu_cotcao_lft()` - Calcula PU a partir de cotação
- `taxa_pu_lft()` - Calcula taxa a partir de PU
- `calcular_lft()` - Função principal

**Side effects:** Nenhum

---

### `titulospub/core/ntnf/calculo_ntnf.py`

**Responsabilidade:** Funções puras de cálculo para NTN-F.

**O que faz:**
- `taxa_pu_ntnf()` - Calcula PU a partir de taxa
- `calculo_dv01_ntnf()` - Calcula DV01
- `calculo_carrego_ntnf()` - Calcula carregamento
- `calcular_ntnf()` - Função principal

**Side effects:** Nenhum

---

### `titulospub/core/di/calculo_di.py`

**Responsabilidade:** Funções puras de cálculo para contratos DI.

**O que faz:**
- `taxa_pu_di()` - Calcula PU a partir de taxa DI
- `calculo_dv01_di()` - Calcula DV01 de contrato DI

**Side effects:** Nenhum

---

### `titulospub/core/dap/calculo_dap.py`

**Responsabilidade:** Funções puras de cálculo para contratos DAP.

**O que faz:**
- `dia_15_do_mes()` - Retorna dia 15 do mês (vencimento DAP)
- `calculo_prt()` - Calcula PRT (Preço de Referência de Títulos)
- `calculo_pu_dap()` - Calcula PU de contrato DAP
- `calculo_financeiro_dap()` - Calcula valor financeiro de contrato DAP
- `dv01_dap()` - Calcula DV01 de contrato DAP

**Side effects:** Nenhum

---

### `titulospub/core/ntnb/vna_ntnb.py`

**Responsabilidade:** Cálculo de VNA (Valor Nominal Ajustado) para NTN-B.

**O que faz:**
- `calculo_vna_ntnb()` - Calcula VNA base
- `calculo_vna_ajustado_ntnb()` - Calcula VNA ajustado para data de liquidação
- `fator_ipca()` - Calcula fator de correção IPCA

**Dependências relevantes:**
- `titulospub.dados.ipca` - Para dados de IPCA

**Side effects:** Nenhum (recebe dados como parâmetro)

---

### `titulospub/core/ntnb/cash_flow_ntnb.py`

**Responsabilidade:** Cálculo de fluxo de caixa (cupons) para NTN-B.

**O que faz:**
- `datas_pagamento_cupons()` - Calcula datas de pagamento de cupons
- `fv_cupons()` - Calcula valor futuro dos cupons
- `calcular_pv_cupons()` - Calcula valor presente dos cupons
- `cash_flow_ntnb()` - Função principal que retorna fluxo completo

**Side effects:** Nenhum

---

### `titulospub/core/ntnf/cash_flow_ntnf.py`

**Responsabilidade:** Cálculo de fluxo de caixa (cupons) para NTN-F.

**O que faz:**
- `f_v_ntnf()` - Calcula valor futuro dos cupons NTNF
- `cotacao_ntnf()` - Calcula cotação baseada em fluxo

**Side effects:** Nenhum

---

### `titulospub/core/auxilio.py`

**Responsabilidade:** Funções auxiliares usadas por múltiplos módulos.

**O que faz:**
- `calculo_pu_carregado()` - Calcula PU carregado genérico
- `codigo_vencimento_bmf()` - Converte código BMF para data de vencimento
- `vencimento_codigo_bmf()` - Converte data de vencimento para código BMF

**Side effects:** Nenhum

---

### `titulospub/utils/datas.py`

**Responsabilidade:** Funções de manipulação de datas e dias úteis.

**O que faz:**
- `adicionar_dias_uteis()` - Adiciona N dias úteis a uma data
- `e_dia_util()` - Verifica se uma data é dia útil
- `dias_trabalho_total()` - Calcula total de dias úteis entre duas datas
- `listar_dias_entre_datas()` - Lista dias úteis entre duas datas
- `ajustar_para_proximo_dia_util()` - Ajusta datas para próximo dia útil
- `listar_datas()` - Lista todas as datas entre duas datas
- `data_vencimento_ajustada()` - Ajusta data de vencimento para dia útil
- `datas_pagamento_cupons()` - Calcula datas de pagamento de cupons

**O que NÃO faz:**
- Não faz scraping de feriados (recebe como parâmetro)

**Side effects:** Nenhum

---

### `titulospub/utils/paths.py`

**Responsabilidade:** Construção de caminhos de arquivos.

**O que faz:**
- `path_backup_csv()` - Retorna caminho para arquivo CSV de backup
- `path_backup_pickle()` - Retorna caminho para arquivo pickle de backup
- `path_logs()` - Retorna caminho para arquivo de log

**Side effects:** Nenhum (apenas construção de strings)

---

### `titulospub/utils/carregamento_var_globais.py`

**Responsabilidade:** Funções de carregamento condicional de variáveis globais.

**O que faz:**
- `_carregar_feriados_se_necessario()` - Carrega feriados se None
- `_carrecar_ipca_dict_se_necessario()` - Carrega IPCA dict se None
- `_carrecar_cdi_se_necessario()` - Carrega CDI se None
- `_carregar_vna_lft_se_necessario()` - Carrega VNA LFT se None

**Dependências relevantes:**
- `titulospub.dados.orquestrador` - VariaveisMercado

**Side effects:**
- Pode fazer scraping via VariaveisMercado se necessário

---

### `titulospub/dados/orquestrador.py`

**Responsabilidade:** Orquestrar todas as variáveis de mercado necessárias para cálculos.

**O que faz:**
- Classe `VariaveisMercado` que centraliza acesso a todas variáveis
- Gerencia cache em memória de variáveis
- Tenta fazer scraping primeiro, usa backup se falhar
- Salva dados em cache para evitar scraping repetido
- Método `atualizar_tudo()` atualiza todas variáveis de uma vez

**O que NÃO faz:**
- Não faz scraping diretamente (delega para módulos de scraping)
- Não persiste cache permanentemente (usa módulo cache)

**Dependências relevantes:**
- `titulospub.scraping.*` - Funções de scraping
- `titulospub.dados.backup` - Funções de backup
- `titulospub.dados.cache` - Sistema de cache
- `titulospub.dados.anbimas`, `titulospub.dados.bmf`, `titulospub.dados.ipca` - Processamento

**Side effects:**
- Mantém cache em memória (`_feriados`, `_ipca_dict`, `_cdi`, etc)
- Faz requisições HTTP via scraping
- Lê arquivos Excel via backup
- Escreve/lê arquivos pickle via cache

**Principais métodos:**
- `get_feriados()` - Obtém lista de feriados
- `get_ipca_dict()` - Obtém dicionário de IPCA
- `get_cdi()` - Obtém taxa CDI
- `get_vna_lft()` - Obtém VNA LFT
- `get_anbimas()` - Obtém dados ANBIMA
- `get_bmf()` - Obtém dados BMF
- `atualizar_tudo()` - Atualiza todas variáveis

---

### `titulospub/dados/cache.py`

**Responsabilidade:** Sistema de cache usando arquivos pickle.

**O que faz:**
- `save_cache()` - Salva dados em arquivo pickle
- `load_cache()` - Carrega dados de arquivo pickle
- `clear_cache()` - Remove arquivo de cache

**O que NÃO faz:**
- Não valida dados do cache
- Não gerencia expiração de cache

**Side effects:**
- Leitura/escrita de arquivos no sistema de arquivos

---

### `titulospub/dados/backup.py`

**Responsabilidade:** Funções de backup (fallback quando scraping falha).

**O que faz:**
- `backup_cdi()` - Lê CDI de arquivo Excel
- `backup_feriados()` - Lê feriados de arquivo Excel
- `backup_ipca_fechado()` - Lê IPCA fechado de arquivo Excel
- `backup_ipca_proj()` - Lê IPCA projetado de arquivo Excel
- `backup_anbimas()` - Lê dados ANBIMA de arquivo Excel
- `backup_bmf()` - Lê dados BMF de arquivo Excel

**O que NÃO faz:**
- Não atualiza arquivos Excel automaticamente
- Não valida dados dos arquivos

**Dependências relevantes:**
- Arquivos Excel em `titulospub/dados/backup_excel/`

**Side effects:**
- Leitura de arquivos Excel no sistema de arquivos

---

### `titulospub/dados/anbimas.py`

**Responsabilidade:** Processamento de dados ANBIMA.

**O que faz:**
- `anbimas()` - Processa DataFrame ANBIMA e retorna dicionário por tipo de título
- Normaliza colunas e tipos de dados
- Organiza dados por tipo de título (LTN, LFT, NTN-B, NTN-F)

**O que NÃO faz:**
- Não faz scraping (recebe DataFrame como parâmetro)
- Não persiste dados

**Side effects:** Nenhum

---

### `titulospub/dados/bmf.py`

**Responsabilidade:** Processamento de dados BMF (ajustes DI e DAP).

**O que faz:**
- `ajustes_bmf()` - Processa dados BMF e retorna dicionário com DI e DAP
- `ajustes_bmf_net()` - Processa dados BMF Net
- Normaliza códigos de vencimento
- Ajusta datas de vencimento para dias úteis

**O que NÃO faz:**
- Não faz scraping diretamente (recebe dados como parâmetro)

**Side effects:** Nenhum

---

### `titulospub/dados/ipca.py`

**Responsabilidade:** Processamento de dados IPCA.

**O que faz:**
- `inicio_fim_mes_ipca()` - Calcula início e fim do mês IPCA
- `dicionario_ipca()` - Cria dicionário de IPCA com fatores de correção
- Processa IPCA fechado e projetado
- Calcula fatores de correção para diferentes datas

**O que NÃO faz:**
- Não faz scraping (recebe dados como parâmetro)

**Side effects:** Nenhum

---

### `titulospub/dados/vencimentos.py`

**Responsabilidade:** Obter listas de vencimentos disponíveis para cada tipo de título.

**O que faz:**
- `get_vencimentos_ltn()` - Retorna lista de vencimentos LTN
- `get_vencimentos_lft()` - Retorna lista de vencimentos LFT
- `get_vencimentos_ntnb()` - Retorna lista de vencimentos NTNB
- `get_vencimentos_ntnf()` - Retorna lista de vencimentos NTNF
- `get_codigos_di_disponiveis()` - Retorna lista de códigos DI disponíveis
- `get_todos_vencimentos()` - Retorna todos vencimentos organizados por tipo

**Dependências relevantes:**
- `titulospub.dados.orquestrador` - Para obter dados ANBIMA

**Side effects:**
- Pode fazer scraping via VariaveisMercado se necessário

---

### `titulospub/scraping/anbima_scraping.py`

**Responsabilidade:** Scraping de dados do site ANBIMA.

**O que faz:**
- `scrap_anbimas()` - Scraping de taxas indicativas ANBIMA
- `scrap_cdi()` - Scraping de taxa CDI
- `scrap_feriados()` - Scraping de lista de feriados
- `scrap_proj_ipca()` - Scraping de IPCA projetado
- `scrap_vna_lft()` - Scraping de VNA LFT

**O que NÃO faz:**
- Não processa dados (apenas coleta)
- Não persiste dados

**Side effects:**
- Faz requisições HTTP para sites externos
- Pode falhar se site estiver indisponível

---

### `titulospub/scraping/sidra_scraping.py`

**Responsabilidade:** Scraping de dados IPCA fechado via API SIDRA.

**O que faz:**
- `puxar_valores_ipca_fechado()` - Obtém valores de IPCA fechado via API SIDRA

**Side effects:**
- Faz requisições HTTP para API SIDRA

---

### `titulospub/scraping/bmf_net_scraping.py`

**Responsabilidade:** Scraping de dados BMF Net.

**O que faz:**
- `scrap_bmf_net()` - Scraping de dados BMF Net (ajustes DI e DAP)

**Side effects:**
- Faz requisições HTTP para BMF Net

---

### `titulospub/scraping/uptodata_scraping.py`

**Responsabilidade:** Scraping de ajustes BMF via UpToData.

**O que faz:**
- `definir_caminho_adj_bmf()` - Define caminho de arquivo de ajustes BMF
- `scrap_ajustes_bmf()` - Scraping de ajustes BMF

**Side effects:**
- Faz requisições HTTP para UpToData
- Lê arquivos locais se disponíveis

---

### `api/main.py`

**Responsabilidade:** Aplicação FastAPI principal.

**O que faz:**
- Cria instância da aplicação FastAPI
- Configura CORS
- Registra todos os routers
- Define lifespan events (atualização de mercado na inicialização)
- Define endpoints raiz (`/`) e health check (`/health`)
- Define endpoint admin para forçar atualização (`/atualizar-mercado`)

**O que NÃO faz:**
- Não contém lógica de cálculo
- Não gerencia estado de carteiras diretamente

**Dependências relevantes:**
- `api.routers.*` - Todos os routers
- `titulospub.dados.orquestrador` - Para atualização de mercado
- `api.utils` - Para controle de atualização

**Side effects:**
- Inicia servidor HTTP
- Atualiza variáveis de mercado na inicialização (via lifespan)

---

### `api/models.py`

**Responsabilidade:** Modelos Pydantic para validação de requests e responses.

**O que faz:**
- Define modelos de request para cada tipo de título (LTNRequest, LFTRequest, etc)
- Define modelos de response para cada tipo de título (LTNResponse, LFTResponse, etc)
- Define modelos para carteiras (CarteiraCreateRequest, CarteiraResponse, etc)
- Define modelos para equivalência (EquivalenciaRequest, EquivalenciaResponse)
- Define modelos para vencimentos (VencimentosResponse, etc)

**O que NÃO faz:**
- Não contém lógica de negócio
- Não faz cálculos

**Side effects:** Nenhum

---

### `api/utils.py`

**Responsabilidade:** Utilitários da API.

**O que faz:**
- `serialize_datetime()` - Serializa datetime para string ISO
- `precisa_atualizar_mercado()` - Verifica se precisa atualizar mercado (baseado em arquivo)
- `marcar_atualizado()` - Marca que mercado foi atualizado hoje
- `get_ultima_atualizacao()` - Obtém data da última atualização

**Side effects:**
- Leitura/escrita de arquivo JSON para controle de atualização

---

### `api/routers/ltn.py`

**Responsabilidade:** Endpoints REST para título LTN.

**O que faz:**
- `POST /titulos/ltn` - Cria e calcula título LTN
- Valida request via Pydantic
- Cria instância de LTN
- Converte resultado para response model
- Trata erros e retorna HTTPException

**O que NÃO faz:**
- Não contém lógica de cálculo (delega para classe LTN)

**Dependências relevantes:**
- `titulospub.core.ltn.titulo_ltn` - Classe LTN
- `api.models` - Modelos Pydantic

**Side effects:** Nenhum (apenas processa request/response HTTP)

---

### `api/routers/lft.py`, `api/routers/ntnb.py`, `api/routers/ntnf.py`

**Responsabilidade:** Similar a `ltn.py`, mas para seus respectivos títulos.

**O que faz:**
- Endpoints `POST /titulos/{tipo}` para criar títulos
- Validação e conversão de request/response

---

### `api/routers/equivalencia.py`

**Responsabilidade:** Endpoint de equivalência entre títulos.

**O que faz:**
- `POST /equivalencia` - Calcula equivalência entre dois títulos
- Valida request
- Chama função `equivalencia()` do core
- Retorna quantidade equivalente

---

### `api/routers/vencimentos.py`

**Responsabilidade:** Endpoints de vencimentos disponíveis.

**O que faz:**
- `GET /vencimentos/{tipo}` - Retorna vencimentos de um tipo específico
- `GET /vencimentos/todos` - Retorna todos vencimentos organizados
- `GET /vencimentos/di` - Retorna códigos DI disponíveis

**Dependências relevantes:**
- `titulospub.dados.vencimentos` - Funções de vencimentos

---

### `api/routers/carteiras.py`

**Responsabilidade:** Endpoints de gestão de carteiras.

**O que faz:**
- `POST /carteiras/{tipo}` - Cria nova carteira
- `GET /carteiras/{carteira_id}` - Obtém dados da carteira
- `PUT /carteiras/{carteira_id}/taxa` - Atualiza taxa de um título
- `PUT /carteiras/{carteira_id}/premio-di` - Atualiza prêmio e DI de um título
- `PUT /carteiras/{carteira_id}/dias` - Atualiza dias de liquidação
- `PUT /carteiras/{carteira_id}/quantidade` - Atualiza quantidade de um título

**O que NÃO faz:**
- Não persiste carteiras (mantém em memória)

**Dependências relevantes:**
- Classes de carteiras de `titulospub.core.carteiras`

**Side effects:**
- Mantém carteiras em dicionário global em memória (não thread-safe com múltiplos workers)

---

### `dash_app/app.py`

**Responsabilidade:** Aplicação Dash principal.

**O que faz:**
- Cria instância da aplicação Dash
- Define layout principal (navbar + container de páginas)
- Define callback de routing (renderiza página baseada em URL)
- Exporta `server` para uso com gunicorn

**O que NÃO faz:**
- Não importa `titulospub` diretamente
- Não contém lógica de cálculo

**Dependências relevantes:**
- `dash_app.pages.*` - Páginas da aplicação
- `dash_app.components.navbar` - Componente de navegação

**Side effects:**
- Inicia servidor HTTP Dash

---

### `dash_app/config.py`

**Responsabilidade:** Configurações globais do Dash.

**O que faz:**
- Define `API_URL` (configurável via variável de ambiente)
- Define `APP_TITLE` e `APP_DESCRIPTION`
- Define `PAGES` (dicionário de rotas)

**Side effects:** Nenhum

---

### `dash_app/pages/ltn.py`

**Responsabilidade:** Página de cálculos LTN no Dash.

**O que faz:**
- Define layout da página (tabela editável, inputs, resultados)
- Define callbacks para:
  - Carregar vencimentos
  - Criar/atualizar carteira
  - Atualizar taxa/premio/dias
  - Calcular equivalência
  - Renderizar tabela editável
- Faz chamadas HTTP para API via `dash_app.utils.api`

**O que NÃO faz:**
- Não importa `titulospub` diretamente
- Não faz cálculos diretamente

**Dependências relevantes:**
- `dash_app.utils.api` - Funções HTTP
- `dash_app.utils.carteiras` - Funções de carteiras
- `dash_app.utils.formatacao` - Formatação de números

**Side effects:**
- Faz requisições HTTP para API

---

### `dash_app/pages/lft.py`, `dash_app/pages/ntnb.py`, `dash_app/pages/ntnf.py`

**Responsabilidade:** Similar a `ltn.py`, mas para seus respectivos títulos.

---

### `dash_app/pages/ntnb_hedge.py`

**Responsabilidade:** Página específica para cálculo de hedge DI de NTNB.

**O que faz:**
- Interface para calcular hedge DI de um título NTNB específico
- Faz chamada HTTP para endpoint `/titulos/ntnb/hedge-di`

---

### `dash_app/utils/api.py`

**Responsabilidade:** Funções de chamada HTTP para API.

**O que faz:**
- `get()` - Requisição GET
- `post()` - Requisição POST
- `put()` - Requisição PUT
- Trata erros HTTP

**Side effects:**
- Faz requisições HTTP para API FastAPI

---

### `dash_app/utils/carteiras.py`

**Responsabilidade:** Funções de manipulação de carteiras no frontend.

**O que faz:**
- `criar_carteira()` - Cria carteira via API
- `atualizar_taxa()` - Atualiza taxa via API
- `atualizar_premio_di()` - Atualiza prêmio e DI via API
- `atualizar_dias_liquidacao()` - Atualiza dias via API

**Side effects:**
- Faz requisições HTTP para API

---

### `dash_app/utils/formatacao.py`

**Responsabilidade:** Formatação de números para exibição.

**O que faz:**
- `formatar_taxa_brasileira()` - Formata taxa como porcentagem brasileira
- `formatar_pu_brasileiro()` - Formata PU brasileiro
- `parse_numero_brasileiro()` - Parse de número brasileiro (vírgula decimal)
- `formatar_bps()` - Formata pontos base
- `formatar_dv01()` - Formata DV01
- `formatar_inteiro()` - Formata inteiro
- `formatar_numero_brasileiro()` - Formata número genérico brasileiro

**Side effects:** Nenhum

---

### `dash_app/utils/vencimentos.py`

**Responsabilidade:** Formatação de vencimentos para exibição.

**O que faz:**
- `formatar_data_para_exibicao()` - Formata data para exibição no Dash

**Side effects:** Nenhum

---

### `dash_app/components/navbar.py`

**Responsabilidade:** Componente de navegação (navbar).

**O que faz:**
- Define layout do navbar com links para cada página
- Usa Dash Bootstrap Components

**Side effects:** Nenhum

---

## 5. DOCUMENTAÇÃO POR FUNÇÃO / CLASSE

### Classes de Títulos

#### `NTNB` (titulospub/core/ntnb/titulo_ntnb.py)

**Assinatura:**
```python
class NTNB:
    def __init__(self, data_vencimento_titulo: str, 
                 data_base: str=None, 
                 dias_liquidacao: int=1,
                 taxa: float=None,
                 premio: float=None,
                 quantidade=10000, 
                 cdi: float=None, 
                 ipca_dict: dict=None, 
                 feriados: list=None,
                 variaveis_mercado: VariaveisMercado | None = None)
```

**Propósito:** Representar e calcular todos os atributos de um título NTN-B.

**Parâmetros:**
- `data_vencimento_titulo`: Data de vencimento do título (YYYY-MM-DD)
- `data_base`: Data base para cálculos (default: hoje)
- `dias_liquidacao`: Dias úteis para liquidação (default: 1)
- `taxa`: Taxa de juros anual (%) (opcional, usa ANBIMA se não fornecido)
- `premio`: Prêmio sobre DAP em pontos base (opcional)
- `quantidade`: Quantidade inicial de títulos (default: 10000)
- `cdi`: Taxa CDI (opcional, obtém via VariaveisMercado se não fornecido)
- `ipca_dict`: Dicionário de IPCA (opcional, obtém via VariaveisMercado)
- `feriados`: Lista de feriados (opcional, obtém via VariaveisMercado)
- `variaveis_mercado`: Instância de VariaveisMercado (cria nova se não fornecido)

**Retorno:** Instância de NTNB com todos atributos calculados.

**Suposições importantes:**
- Vencimento deve existir na base ANBIMA
- Taxa é anual e em formato decimal (ex: 7.53 = 7.53%)
- Premio é em pontos base (ex: 0.5 = 50 bps)

**Passo a passo de funcionamento:**
1. Inicializa VariaveisMercado se não fornecido
2. Configura datas (vencimento, base, liquidação)
3. Busca taxa ANBIMA se taxa não fornecida
4. Configura DAP (calcula ajuste DAP)
5. Configura taxa (usa taxa fornecida ou calcula de premio+DAP)
6. Calcula VNA ajustado
7. Calcula PU, DV01, carregamento, duration
8. Calcula hedge DAP

**Onde é utilizada:**
- `api/routers/ntnb.py` - Criação via API
- `titulospub/core/carteiras/carteira_ntnb.py` - Gestão de carteiras
- `titulospub/core/equivalencia.py` - Cálculo de equivalência
- `dash_app/pages/ntnb.py` - Interface web (via API)

**Propriedades principais:**
- `quantidade` (getter/setter) - Quantidade de títulos
- `financeiro` (getter/setter) - Valor financeiro em R$
- `pu_d0` - Preço unitário à vista
- `pu_termo` - Preço unitário a termo
- `dv01` - DV01 (sensibilidade a 1bp)
- `carrego_brl` - Carregamento em reais
- `carrego_bps` - Carregamento em pontos base
- `duration` - Duration de Macaulay
- `hedge_dap` - Quantidade de contratos DAP para hedge

---

#### `LTN` (titulospub/core/ltn/titulo_ltn.py)

**Assinatura:**
```python
class LTN:
    def __init__(self, data_vencimento_titulo: str,
                 data_base: str=None,
                 dias_liquidacao: int=1,
                 taxa: float=None,
                 premio: float=None,
                 di: float=None,
                 quantidade: float=50000,
                 cdi: float=None,
                 feriados: list=None,
                 variaveis_mercado: VariaveisMercado=None)
```

**Propósito:** Representar e calcular todos os atributos de um título LTN.

**Parâmetros:**
- `data_vencimento_titulo`: Data de vencimento (YYYY-MM-DD)
- `data_base`: Data base (default: hoje)
- `dias_liquidacao`: Dias úteis para liquidação (default: 1)
- `taxa`: Taxa anual (%) (opcional)
- `premio`: Prêmio sobre DI em pontos base (opcional)
- `di`: Taxa DI de referência (%) (usado com premio)
- `quantidade`: Quantidade inicial (default: 50000)
- `cdi`: Taxa CDI (opcional)
- `feriados`: Lista de feriados (opcional)
- `variaveis_mercado`: Instância de VariaveisMercado (opcional)

**Retorno:** Instância de LTN com todos atributos calculados.

**Passo a passo:**
1. Inicializa VariaveisMercado
2. Configura datas
3. Busca taxa ANBIMA se não fornecida
4. Calcula taxa de premio+DI se fornecido
5. Calcula PU, DV01, carregamento
6. Calcula hedge DI

**Propriedades principais:**
- `quantidade`, `financeiro`, `pu_d0`, `pu_termo`, `dv01`, `carrego_brl`, `hedge_di`

---

#### `LFT` (titulospub/core/lft/titulo_lft.py)

**Assinatura:**
```python
class LFT:
    def __init__(self, data_vencimento_titulo: str,
                 data_base: str=None,
                 dias_liquidacao: int=1,
                 taxa: float=None,
                 quantidade: float=10000,
                 cdi: float=None,
                 vna_lft: float=None,
                 feriados: list=None,
                 variaveis_mercado: VariaveisMercado=None)
```

**Propósito:** Representar e calcular todos os atributos de um título LFT.

**Nota:** LFT não tem DV01 pois é pós-fixado (não tem sensibilidade a taxa prefixada).

**Propriedades principais:**
- `quantidade`, `financeiro`, `pu_d0`, `pu_termo`, `cotacao`, `vna_ajustado`

---

#### `NTNF` (titulospub/core/ntnf/titulo_ntnf.py)

**Assinatura:**
```python
class NTNF:
    def __init__(self, data_vencimento_titulo: str,
                 data_base: str=None,
                 dias_liquidacao: int=1,
                 taxa: float=None,
                 premio: float=None,
                 di: float=None,
                 quantidade: float=50000,
                 cdi: float=None,
                 feriados: list=None,
                 variaveis_mercado: VariaveisMercado=None)
```

**Propósito:** Similar a LTN, mas para NTN-F (com cupons semestrais).

**Propriedades principais:**
- `quantidade`, `financeiro`, `pu_d0`, `pu_termo`, `dv01`, `carrego_brl`, `hedge_di`

---

#### `DI` (titulospub/core/di/di_contrato.py)

**Assinatura:**
```python
class DI:
    def __init__(self, codigo: str,
                 taxa: float=None,
                 quantidade: float=1000,
                 data_liquidacao: pd.Timestamp=None,
                 data_vencimento: pd.Timestamp=None,
                 feriados: list=None)
```

**Propósito:** Representar contrato DI (Depósito Interbancário).

**Parâmetros:**
- `codigo`: Código do contrato DI (ex: "DI1F32")
- `taxa`: Taxa DI (%) (opcional, busca de BMF se não fornecido)
- `quantidade`: Quantidade de contratos (default: 1000)

**Propriedades principais:**
- `quantidade`, `financeiro`, `pu`, `dv01`

---

### Funções de Cálculo

#### `equivalencia()` (titulospub/core/equivalencia.py)

**Assinatura:**
```python
def equivalencia(titulo1: str, venc1: str,
                 titulo2: str, venc2: str,
                 qtd1: float,
                 criterio: str='dv',
                 tx1: float=None,
                 tx2: float=None) -> float
```

**Propósito:** Calcular quantidade equivalente de um título baseado em outro.

**Parâmetros:**
- `titulo1`: Tipo do primeiro título ('LTN', 'LFT', 'NTNB', 'NTNF')
- `venc1`: Vencimento do primeiro título (YYYY-MM-DD)
- `titulo2`: Tipo do segundo título
- `venc2`: Vencimento do segundo título
- `qtd1`: Quantidade do primeiro título
- `criterio`: 'dv' (DV01) ou 'fin' (financeiro)
- `tx1`: Taxa do primeiro título (opcional)
- `tx2`: Taxa do segundo título (opcional)

**Retorno:** Quantidade equivalente do segundo título (float).

**Passo a passo:**
1. Cria instância do primeiro título com quantidade qtd1
2. Calcula métrica (DV01 ou financeiro) do primeiro título
3. Cria instância do segundo título
4. Calcula quantidade do segundo título que resulta na mesma métrica

**Onde é utilizada:**
- `api/routers/equivalencia.py` - Endpoint de equivalência
- `dash_app/pages/*.py` - Interface web (via API)

---

#### `calculo_ntnb()` (titulospub/core/ntnb/calculo_ntnb.py)

**Assinatura:**
```python
def calculo_ntnb(data, data_liquidacao, data_vencimento, taxa,
                  cdi=None, ipca_dict=None, feriados=None)
```

**Propósito:** Função principal de cálculo de NTN-B. Calcula todos os valores derivados.

**Retorno:** Dicionário com todos os valores calculados (PU, DV01, duration, etc).

**Passo a passo:**
1. Calcula fluxo de cupons
2. Calcula VNA ajustado
3. Calcula PU à vista
4. Calcula PU a termo
5. Calcula duration
6. Calcula DV01
7. Calcula PU carregado
8. Calcula PU ajustado
9. Calcula carregamento

---

#### `calculo_vna_ajustado_ntnb()` (titulospub/core/ntnb/vna_ntnb.py)

**Assinatura:**
```python
def calculo_vna_ajustado_ntnb(data: pd.Timestamp,
                               data_liquidacao: pd.Timestamp,
                               ipca_dict: dict=None,
                               feriados: list=None,
                               leilao=False) -> float
```

**Propósito:** Calcular VNA (Valor Nominal Ajustado) ajustado para data de liquidação.

**Parâmetros:**
- `data`: Data base
- `data_liquidacao`: Data de liquidação
- `ipca_dict`: Dicionário de IPCA (opcional)
- `feriados`: Lista de feriados (opcional)
- `leilao`: Se True, usa regra de leilão (default: False)

**Retorno:** VNA ajustado (float).

**Passo a passo:**
1. Calcula VNA base para data
2. Calcula fator IPCA entre data e liquidação
3. Ajusta VNA pelo fator IPCA

---

### Classes de Carteiras

#### `CarteiraNTNB` (titulospub/core/carteiras/carteira_ntnb.py)

**Assinatura:**
```python
class CarteiraNTNB:
    def __init__(self, data_base: str=None,
                 dias_liquidacao: int=1,
                 quantidade_padrao: float=None)
```

**Propósito:** Gerenciar carteira de múltiplos títulos NTN-B.

**Métodos principais:**
- `adicionar_titulo()` - Adiciona título à carteira
- `remover_titulo()` - Remove título da carteira
- `atualizar_taxa()` - Atualiza taxa de um título específico
- `atualizar_dias_liquidacao()` - Atualiza dias de liquidação globalmente
- `get_dados()` - Retorna dados formatados da carteira
- `get_total_quantidade()` - Retorna quantidade total
- `get_total_financeiro()` - Retorna financeiro total
- `get_total_dv01()` - Retorna DV01 total

**Side effects:**
- Mantém estado em memória (dicionário de títulos)

---

### Classe de Orquestração

#### `VariaveisMercado` (titulospub/dados/orquestrador.py)

**Assinatura:**
```python
class VariaveisMercado:
    def __init__(self)
```

**Propósito:** Orquestrar todas as variáveis de mercado necessárias para cálculos.

**Métodos principais:**
- `get_feriados(force_update=False)` - Obtém lista de feriados
- `get_ipca_dict(data=None, feriados=None, force_update=False)` - Obtém dicionário IPCA
- `get_cdi(force_update=False)` - Obtém taxa CDI
- `get_vna_lft(force_update=False)` - Obtém VNA LFT
- `get_anbimas(force_update=False)` - Obtém dados ANBIMA
- `get_bmf(force_update=False)` - Obtém dados BMF
- `atualizar_tudo(verbose=False)` - Atualiza todas variáveis

**Estratégia de obtenção de dados:**
1. Verifica cache em memória (se disponível e não force_update)
2. Verifica cache em arquivo (se disponível e não force_update)
3. Tenta fazer scraping
4. Se scraping falhar, usa backup (arquivos Excel)
5. Salva em cache (memória e arquivo)

**Side effects:**
- Mantém cache em memória
- Faz requisições HTTP (scraping)
- Lê arquivos Excel (backup)
- Escreve/lê arquivos pickle (cache)

---

## 6. FLUXO DE EXECUÇÃO

### Inicialização da API

1. `run_api.py` executa
2. `api/main.py` cria aplicação FastAPI
3. Lifespan event (`lifespan()`) executa:
   - Verifica se precisa atualizar mercado (`precisa_atualizar_mercado()`)
   - Se sim, cria `VariaveisMercado()` e chama `atualizar_tudo()`
   - Marca como atualizado (`marcar_atualizado()`)
4. Registra routers
5. Inicia servidor uvicorn

### Requisição de Cálculo de Título

1. Cliente faz `POST /titulos/ltn` com dados
2. `api/routers/ltn.py` recebe request
3. Valida request via Pydantic (`LTNRequest`)
4. Cria instância `LTN(**kwargs)`
5. `LTN.__init__()` executa:
   - Cria `VariaveisMercado()` (ou usa fornecido)
   - Obtém variáveis de mercado (feriados, CDI, etc)
   - Busca taxa ANBIMA se não fornecida
   - Calcula todos atributos
6. Converte resultado para `LTNResponse`
7. Retorna JSON

### Requisição de Criação de Carteira

1. Cliente faz `POST /carteiras/ltn`
2. `api/routers/carteiras.py` recebe request
3. Cria instância `CarteiraLTN()`
4. Obtém vencimentos disponíveis via `get_vencimentos_ltn()`
5. Para cada vencimento, cria título e adiciona à carteira
6. Armazena carteira em dicionário global (com ID único)
7. Retorna `CarteiraResponse` com dados da carteira

### Inicialização do Dash

1. `run_dash_app.py` executa
2. `dash_app/app.py` cria aplicação Dash
3. Define layout (navbar + container)
4. Define callback de routing
5. Inicia servidor Dash

### Interação no Dash (Exemplo: LTN)

1. Usuário acessa `/ltn`
2. Callback `render_page()` renderiza `ltn.layout()`
3. Layout carrega vencimentos via `GET /vencimentos/ltn` (chamada HTTP)
4. Usuário cria carteira (botão)
5. Callback faz `POST /carteiras/ltn` (chamada HTTP)
6. API cria carteira e retorna dados
7. Callback atualiza tabela com dados da carteira
8. Usuário edita taxa em tabela
9. Callback faz `PUT /carteiras/{id}/taxa` (chamada HTTP)
10. API atualiza título na carteira e retorna dados atualizados
11. Callback atualiza tabela

---

## 7. SUPOSIÇÕES E RISCOS TÉCNICOS

### Suposições Implícitas

1. **Dados de mercado sempre disponíveis:**
   - Sistema assume que sempre consegue obter dados (scraping ou backup)
   - Se ambos falharem, sistema pode quebrar

2. **Formato de datas:**
   - Datas sempre em formato YYYY-MM-DD (string) ou pd.Timestamp
   - Feriados sempre em formato compatível

3. **Taxas em formato decimal:**
   - Taxas sempre em porcentagem (ex: 12.5 = 12.5%)
   - Premios sempre em pontos base (ex: 0.5 = 50 bps)

4. **Vencimentos válidos:**
   - Vencimentos sempre existem na base ANBIMA
   - Se não existir, sistema lança ValueError

5. **Estado de carteiras:**
   - Carteiras mantidas em memória (não persistem entre reinicializações)
   - Com múltiplos workers, cada worker tem seu próprio estado

### Riscos Técnicos

1. **Scraping pode falhar:**
   - Sites externos podem estar indisponíveis
   - Estrutura HTML pode mudar
   - **Mitigação:** Sistema usa backup quando scraping falha

2. **Cache pode ficar desatualizado:**
   - Cache não tem expiração automática
   - Dados podem ficar antigos se não atualizar manualmente
   - **Mitigação:** API atualiza automaticamente na inicialização (uma vez por dia)

3. **Carteiras em memória:**
   - Perdidas se servidor reiniciar
   - Não compartilhadas entre múltiplos workers
   - **Mitigação:** Documentado no código, migração para banco/Redis recomendada

4. **Thread-safety:**
   - `VariaveisMercado` mantém cache em memória (pode ter problemas com múltiplos workers)
   - Carteiras em dicionário global (não thread-safe)
   - **Mitigação:** Por padrão usa 1 worker, múltiplos workers requerem migração

5. **Dependência de bibliotecas externas:**
   - Pandas, requests, etc podem ter breaking changes
   - **Mitigação:** Versões fixadas em requirements.txt

---

## 8. PADRÕES E CONVENÇÕES

### Nomenclatura

- **Classes:** PascalCase (ex: `NTNB`, `VariaveisMercado`)
- **Funções:** snake_case (ex: `calculo_ntnb`, `get_feriados`)
- **Variáveis privadas:** Prefixo `_` (ex: `_quantidade`, `_feriados`)
- **Módulos:** snake_case (ex: `titulo_ntnb.py`, `calculo_ltn.py`)

### Estrutura de Classes de Títulos

Todas classes de títulos seguem padrão similar:
1. `__init__()` - Inicialização com parâmetros
2. Métodos privados `_configurar_*()` - Configuração interna
3. Método `_calcular()` - Executa cálculos
4. Propriedades `@property` - Acesso a atributos calculados
5. Setters para `quantidade` e `financeiro` - Atualização de posição

### Tratamento de Erros

- **Validação:** Via Pydantic na API
- **Erros de cálculo:** ValueError com mensagem descritiva
- **Erros de scraping:** Try/except com fallback para backup
- **Erros HTTP:** HTTPException na API

### Cache

- Cache em memória (atributos `_*` em `VariaveisMercado`)
- Cache em arquivo (pickle via `cache.py`)
- Cache verificado antes de fazer scraping
- Cache atualizado após scraping bem-sucedido

---

## FIM DA DOCUMENTAÇÃO

Este documento cobre toda a estrutura, funcionamento e detalhes do codebase. Para informações específicas sobre funções individuais, consulte os docstrings nos arquivos fonte.
