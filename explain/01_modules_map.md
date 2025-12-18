# Mapa de Módulos - Calculadora de Títulos Públicos

Lista completa de todos os módulos Python do projeto, com descrição de uma linha.

## Camada de Domínio (`titulospub/`)

### Módulo Principal
- `titulospub/__init__.py` - Ponto de entrada, exporta todas classes e funções públicas

### Core - Classes de Títulos
- `titulospub/core/__init__.py` - Exporta classes NTNB, LTN, LFT, NTNF, DI
- `titulospub/core/ntnb/titulo_ntnb.py` - Classe NTNB (título indexado ao IPCA)
- `titulospub/core/ltn/titulo_ltn.py` - Classe LTN (título prefixado)
- `titulospub/core/lft/titulo_lft.py` - Classe LFT (título pós-fixado Selic)
- `titulospub/core/ntnf/titulo_ntnf.py` - Classe NTNF (título prefixado com cupom)
- `titulospub/core/di/di_contrato.py` - Classe DI (contrato de depósito interbancário)

### Core - Funções de Cálculo
- `titulospub/core/ntnb/calculo_ntnb.py` - Funções puras de cálculo NTNB (PU, DV01, duration)
- `titulospub/core/ltn/calculo_ltn.py` - Funções puras de cálculo LTN (PU, DV01)
- `titulospub/core/lft/calculo_lft.py` - Funções puras de cálculo LFT (PU, cotação)
- `titulospub/core/ntnf/calculo_ntnf.py` - Funções puras de cálculo NTNF (PU, DV01)
- `titulospub/core/di/calculo_di.py` - Funções puras de cálculo DI (PU, DV01)
- `titulospub/core/dap/calculo_dap.py` - Funções puras de cálculo DAP (PU, DV01, financeiro)

### Core - Cálculos Auxiliares
- `titulospub/core/ntnb/vna_ntnb.py` - Cálculo de VNA (Valor Nominal Ajustado) NTNB
- `titulospub/core/ntnb/cash_flow_ntnb.py` - Cálculo de fluxo de caixa (cupons) NTNB
- `titulospub/core/ntnf/cash_flow_ntnf.py` - Cálculo de fluxo de caixa (cupons) NTNF
- `titulospub/core/lft/ajuste_vna_lft.py` - Cálculo de VNA ajustado LFT
- `titulospub/core/auxilio.py` - Funções auxiliares (códigos BMF, PU carregado)
- `titulospub/core/equivalencia.py` - Função de equivalência entre títulos

### Core - Carteiras
- `titulospub/core/carteiras/__init__.py` - Exporta classes de carteiras
- `titulospub/core/carteiras/carteira_ntnb.py` - Carteira de títulos NTNB
- `titulospub/core/carteiras/carteira_ltn.py` - Carteira de títulos LTN
- `titulospub/core/carteiras/carteira_lft.py` - Carteira de títulos LFT
- `titulospub/core/carteiras/carteira_ntnf.py` - Carteira de títulos NTNF

### Dados - Orquestração
- `titulospub/dados/__init__.py` - Exporta funções de backup, cache, VariaveisMercado
- `titulospub/dados/orquestrador.py` - Classe VariaveisMercado (orquestra todas variáveis)
- `titulospub/dados/cache.py` - Sistema de cache (save/load/clear arquivos pickle)
- `titulospub/dados/backup.py` - Funções de backup (leitura de arquivos Excel)
- `titulospub/dados/anbimas.py` - Processamento de dados ANBIMA
- `titulospub/dados/bmf.py` - Processamento de dados BMF (ajustes DI e DAP)
- `titulospub/dados/ipca.py` - Processamento de dados IPCA (fatores de correção)
- `titulospub/dados/vencimentos.py` - Funções para obter vencimentos disponíveis

### Scraping
- `titulospub/scraping/__init__.py` - Exporta funções de scraping
- `titulospub/scraping/anbima_scraping.py` - Scraping de dados ANBIMA (taxas, CDI, feriados, IPCA proj, VNA LFT)
- `titulospub/scraping/sidra_scraping.py` - Scraping de dados IPCA fechado via API SIDRA
- `titulospub/scraping/bmf_net_scraping.py` - Scraping de dados BMF Net (ajustes DI e DAP)
- `titulospub/scraping/uptodata_scraping.py` - Scraping de ajustes BMF via UpToData

### Utils
- `titulospub/utils/__init__.py` - Exporta funções utilitárias
- `titulospub/utils/datas.py` - Funções de manipulação de datas (dias úteis, feriados)
- `titulospub/utils/paths.py` - Funções para construção de caminhos de arquivos
- `titulospub/utils/carregamento_var_globais.py` - Funções de carregamento condicional de variáveis

## Camada de API (`api/`)

- `api/__init__.py` - Módulo vazio
- `api/main.py` - Aplicação FastAPI principal (cria app, registra routers, lifespan events)
- `api/models.py` - Modelos Pydantic (Request/Response para todos endpoints)
- `api/utils.py` - Utilitários da API (serialização, controle de atualização)

### Routers
- `api/routers/__init__.py` - Módulo vazio
- `api/routers/ltn.py` - Endpoints de título LTN (POST /titulos/ltn)
- `api/routers/lft.py` - Endpoints de título LFT (POST /titulos/lft)
- `api/routers/ntnb.py` - Endpoints de título NTNB (POST /titulos/ntnb, POST /titulos/ntnb/hedge-di)
- `api/routers/ntnf.py` - Endpoints de título NTNF (POST /titulos/ntnf)
- `api/routers/equivalencia.py` - Endpoint de equivalência (POST /equivalencia)
- `api/routers/vencimentos.py` - Endpoints de vencimentos (GET /vencimentos/*)
- `api/routers/carteiras.py` - Endpoints de carteiras (POST/GET/PUT /carteiras/*)

## Camada de Frontend (`dash_app/`)

- `dash_app/__init__.py` - Módulo vazio
- `dash_app/app.py` - Aplicação Dash principal (layout, routing)
- `dash_app/config.py` - Configurações globais (API_URL, título, rotas)

### Components
- `dash_app/components/__init__.py` - Módulo vazio
- `dash_app/components/navbar.py` - Componente de navegação (navbar)

### Pages
- `dash_app/pages/__init__.py` - Módulo vazio
- `dash_app/pages/home.py` - Página inicial
- `dash_app/pages/ltn.py` - Página de cálculos LTN (tabela editável)
- `dash_app/pages/lft.py` - Página de cálculos LFT (tabela editável)
- `dash_app/pages/ntnb.py` - Página de cálculos NTNB (tabela editável)
- `dash_app/pages/ntnb_hedge.py` - Página de hedge DI para NTNB
- `dash_app/pages/ntnf.py` - Página de cálculos NTNF (tabela editável)

### Utils
- `dash_app/utils/__init__.py` - Módulo vazio
- `dash_app/utils/api.py` - Funções de chamada HTTP para API (get, post, put)
- `dash_app/utils/carteiras.py` - Funções de manipulação de carteiras (criar, atualizar)
- `dash_app/utils/formatacao.py` - Funções de formatação de números (taxas, PU, DV01)
- `dash_app/utils/vencimentos.py` - Funções de formatação de vencimentos

## Scripts de Execução

- `run_api.py` - Script para iniciar API FastAPI (uvicorn)
- `run_dash_app.py` - Script para iniciar aplicação Dash

## Configuração

- `setup.py` - Configuração do pacote Python
- `pyproject.toml` - Metadados do projeto
- `MANIFEST.in` - Arquivos a incluir no pacote
- `requirements.txt` - Dependências do projeto
- `.gitignore` - Arquivos ignorados pelo Git

## Documentação

- `README.md` - Documentação básica do projeto
- `RUNBOOK.md` - Guia de execução em rede interna
- `DOCS_CODEBASE.md` - Documentação completa do codebase
