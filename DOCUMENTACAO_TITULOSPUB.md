# Documentação Completa do Módulo titulospub

> **Documento de Referência Técnica**  
> Este documento descreve em detalhes o funcionamento interno do módulo `titulospub`, incluindo arquitetura, fluxos de dados, padrões de código e oportunidades de refatoração.  
> Útil para desenvolvedores que precisam entender o sistema para refatoração, manutenção ou extensão.

## Índice

1. [Resumo Executivo](#resumo-executivo)
2. [Visão Geral](#visão-geral)
3. [Estrutura do Módulo](#estrutura-do-módulo)
4. [Arquitetura e Fluxo de Dados](#arquitetura-e-fluxo-de-dados)
5. [Componentes Principais](#componentes-principais)
   - [5.1. Core - Classes de Títulos](#51-core---classes-de-títulos)
   - [5.2. Dados - Sistema de Dados de Mercado](#52-dados---sistema-de-dados-de-mercado)
   - [5.3. Scraping - Coleta de Dados](#53-scraping---coleta-de-dados)
   - [5.4. Utils - Utilitários](#54-utils---utilitários)
6. [Detalhamento por Tipo de Título](#detalhamento-por-tipo-de-título)
7. [Padrões e Convenções](#padrões-e-convenções)
8. [Dependências e Integrações](#dependências-e-integrações)
9. [Pontos de Atenção para Refatoração](#pontos-de-atenção-para-refatoração)
10. [Guia Rápido de Referência](#guia-rápido-de-referência)

---

## Resumo Executivo

### O Que É Este Módulo?

O `titulospub` é um sistema Python para cálculo e análise de **títulos públicos brasileiros**. Ele permite:

- Criar e calcular métricas de 5 tipos de títulos (NTNB, LTN, LFT, NTNF, DI)
- Obter dados de mercado automaticamente (ANBIMA, BMF, IPCA, CDI)
- Calcular valores como PU, DV01, carregamento, duration, hedge
- Trabalhar com posições por quantidade ou valor financeiro

### Arquitetura Atual

```
┌─────────────────────────────────────────────────────────┐
│                    Classes de Título                    │
│              (NTNB, LTN, LFT, NTNF, DI)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              VariaveisMercado                          │
│            (Orquestrador de Dados)                     │
└─────┬───────────────────────┬──────────────────────────┘
      │                       │
      ▼                       ▼
┌─────────────┐      ┌──────────────────┐
│   Scraping  │      │  Cache + Backup  │
│  (Web APIs) │      │   (Pickle/Excel) │
└─────────────┘      └──────────────────┘
```

### Principais Problemas Identificados

1. **Acoplamento Forte**: Classes de título dependem diretamente de `VariaveisMercado`
2. **Código Duplicado**: Muitos métodos idênticos entre classes (configuração de datas, ajuste de valores)
3. **Falta de Abstrações**: Sem interfaces para acesso a dados, difícil testar
4. **Estado Global**: `VariaveisMercado` mantém estado em memória
5. **Mistura de Responsabilidades**: Lógica de negócio misturada com acesso a dados

### Oportunidades de Refatoração

1. **Criar Interface de Repositório**: Separar domínio de dados através de `MarketDataRepository`
2. **Classe Base para Títulos**: Consolidar código comum em `TituloBase`
3. **Funções Generalizadas**: Unificar cálculos similares (carrego, DV01)
4. **Injeção de Dependência**: Tornar dependências explícitas
5. **Testabilidade**: Facilitar criação de mocks e testes unitários

---

## Visão Geral

O módulo `titulospub` é um sistema completo para cálculo e análise de títulos públicos brasileiros. Ele fornece:

- **Classes de títulos**: NTNB, LTN, LFT, NTNF, DI
- **Cálculos financeiros**: PU, DV01, carregamento, duration, hedge
- **Coleta de dados**: Scraping de ANBIMA, BMF, IPCA, CDI
- **Gerenciamento de dados**: Cache, backup, orquestração de variáveis de mercado
- **Utilitários**: Manipulação de datas, caminhos, carregamento de variáveis

### Características Principais

- **Cálculos determinísticos**: Mesmos inputs produzem mesmos outputs
- **Suporte a múltiplos títulos**: 5 tipos diferentes de títulos públicos
- **Flexibilidade de posicionamento**: Por quantidade ou valor financeiro
- **Integração com dados de mercado**: ANBIMA, BMF, IPCA, CDI
- **Sistema de cache**: Otimização de performance
- **Fallback para backups**: Resiliência em caso de falha no scraping

---

## Estrutura do Módulo

```
titulospub/
├── __init__.py                 # Ponto de entrada principal
├── core/                       # Lógica de negócio - Classes de títulos
│   ├── __init__.py
│   ├── auxilio.py             # Funções auxiliares compartilhadas
│   ├── equivalencia.py        # Cálculo de equivalência entre títulos
│   ├── ntnb/                  # Títulos NTN-B (Indexados ao IPCA)
│   │   ├── titulo_ntnb.py    # Classe principal NTNB
│   │   ├── calculo_ntnb.py   # Funções de cálculo
│   │   ├── cash_flow_ntnb.py # Cálculo de fluxo de caixa
│   │   └── vna_ntnb.py       # Cálculo de VNA (Valor Nominal Ajustado)
│   ├── ltn/                   # Letras do Tesouro Nacional
│   │   ├── titulo_ltn.py
│   │   └── calculo_ltn.py
│   ├── lft/                   # Letras Financeiras do Tesouro
│   │   ├── titulo_lft.py
│   │   ├── calculo_lft.py
│   │   └── ajuste_vna_lft.py
│   ├── ntnf/                  # Notas do Tesouro Nacional - Série F
│   │   ├── titulo_ntnf.py
│   │   ├── calculo_ntnf.py
│   │   └── cash_flow_ntnf.py
│   ├── di/                    # Contratos de Depósito Interbancário
│   │   ├── di_contrato.py
│   │   └── calculo_di.py
│   ├── dap/                   # Cálculos relacionados a DAP
│   │   └── calculo_dap.py
│   └── carteiras/            # Classes para gestão de carteiras
│       ├── carteira_ntnb.py
│       ├── carteira_ltn.py
│       ├── carteira_lft.py
│       └── carteira_ntnf.py
├── dados/                     # Camada de acesso a dados
│   ├── __init__.py
│   ├── orquestrador.py       # VariaveisMercado - Orquestrador principal
│   ├── anbimas.py            # Processamento de dados ANBIMA
│   ├── bmf.py                # Processamento de dados BMF
│   ├── ipca.py               # Processamento de dados IPCA
│   ├── cache.py              # Sistema de cache (pickle)
│   ├── backup.py             # Funções de backup (Excel)
│   └── backup_excel/         # Arquivos Excel de backup
├── scraping/                  # Coleta de dados via web scraping
│   ├── __init__.py
│   ├── anbima_scraping.py    # Scraping ANBIMA
│   ├── sidra_scraping.py     # Scraping IPCA (SIDRA/IBGE)
│   ├── uptodata_scraping.py  # Scraping BMF (UpToData)
│   └── bmf_net_scraping.py   # Scraping BMF alternativo
└── utils/                     # Utilitários
    ├── __init__.py
    ├── datas.py              # Funções de manipulação de datas
    ├── paths.py              # Gerenciamento de caminhos
    └── carregamento_var_globais.py  # Carregamento lazy de variáveis
```

---

## Arquitetura e Fluxo de Dados

### Fluxo Principal

```
┌─────────────────┐
│   Usuário/API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classes Título │  (NTNB, LTN, LFT, NTNF, DI)
│   (core/*.py)   │
└────────┬────────┘
         │
         │ Requisita dados
         ▼
┌─────────────────┐
│ VariaveisMercado│  (dados/orquestrador.py)
│  (Orquestrador) │
└────────┬────────┘
         │
         ├──► Cache (pickle) ──┐
         │                      │
         ├──► Scraping ─────────┤
         │                      │
         └──► Backup (Excel) ───┘
```

### Camadas de Responsabilidade

1. **Camada de Domínio (core/)**: Contém toda a lógica de negócio
   - Classes de títulos
   - Cálculos financeiros
   - Regras de negócio

2. **Camada de Dados (dados/)**: Gerencia acesso a dados de mercado
   - Orquestrador (`VariaveisMercado`)
   - Processamento de dados brutos
   - Sistema de cache e backup

3. **Camada de Coleta (scraping/)**: Coleta dados de fontes externas
   - Web scraping
   - Parsing de dados

4. **Camada de Utilitários (utils/)**: Funções auxiliares
   - Manipulação de datas
   - Gerenciamento de arquivos
   - Carregamento lazy

---

## Componentes Principais

### 4.1. Core - Classes de Títulos

#### Estrutura Comum das Classes de Título

Todas as classes de título seguem um padrão similar:

```python
class Titulo:
    def __init__(self, data_vencimento_titulo, data_base=None, 
                 dias_liquidacao=1, taxa=None, quantidade=..., 
                 variaveis_mercado=None):
        # 1. Inicialização de VariaveisMercado
        self._vm = variaveis_mercado or VariaveisMercado()
        
        # 2. Carregamento de dados de mercado (com fallback)
        self._feriados = feriados or self._vm.get_feriados()
        self._cdi = cdi or self._vm.get_cdi()
        
        # 3. Configuração de datas
        self._configurar_datas(...)
        
        # 4. Configuração do título (busca ANBIMA/BMF)
        self._configurar_titulo()
        
        # 5. Configuração de taxa
        self._configurar_taxa()
        
        # 6. Cálculos iniciais
        self._calcular()
    
    # Propriedades mutáveis (com setters que recalculam)
    @property
    def taxa(self): ...
    @taxa.setter
    def taxa(self, v): ...
    
    @property
    def quantidade(self): ...
    @quantidade.setter
    def quantidade(self, v): ...
    
    @property
    def financeiro(self): ...
    @financeiro.setter
    def financeiro(self, v): ...
    
    # Método principal de cálculo
    def _calcular(self): ...
```

#### Padrões Repetidos Identificados

1. **`_configurar_datas()`**: Idêntico em NTNB, LTN, NTNF
   - Converte datas para pandas Timestamp
   - Calcula data de liquidação baseada em dias úteis
   - Normaliza datas

2. **`_configurar_titulo()`**: Padrão similar em todos
   - Busca dados ANBIMA/BMF para o vencimento
   - Valida existência do título
   - Extrai taxa padrão

3. **`_ajustar_valores_para_quantidade()`**: Código duplicado
   - Normaliza valores para unidade
   - Atualiza quantidade
   - Reaplica multiplicação

4. **`_ajustar_valores_para_financeiro()`**: Código duplicado
   - Normaliza valores para unidade
   - Calcula nova quantidade
   - Reaplica multiplicação

5. **Propriedades comuns**: `taxa`, `quantidade`, `financeiro`, `data_base`, `data_liquidacao`

#### NTNB (Títulos Indexados ao IPCA)

**Características**:
- Indexado ao IPCA
- Cupom semestral (6% a.a.)
- Requer dados de IPCA e VNA

**Cálculos Específicos**:
- `calculo_vna_ajustado_ntnb()`: Calcula VNA ajustado para data de liquidação
- `cash_flow_ntnb()`: Gera fluxo de cupons semestrais
- `calculo_duration()`: Calcula duration do título
- `calculo_pu_ajustado()`: PU ajustado pelo IPCA
- `calculo_hedge_dap()`: Hedge usando contratos DAP

**Dependências de Dados**:
- IPCA (fechado e projeção)
- VNA base
- DAP para hedge

**Exemplo de Uso**:
```python
ntnb = NTNB("2035-05-15", taxa=7.53)
ntnb.financeiro = 100000  # Define posição por valor
print(f"PU: {ntnb.pu_termo:.6f}")
print(f"DV01: {ntnb.dv01:.2f}")
print(f"Hedge DAP: {ntnb.hedge_dap}")
```

#### LTN (Letras do Tesouro Nacional)

**Características**:
- Prefixado
- Zero cupom
- Vencimento em data específica

**Cálculos Específicos**:
- `taxa_pu_ltn()`: Converte taxa em PU
- `pu_taxa_ltn()`: Converte PU em taxa
- `calculo_dv01_ltn()`: DV01 por diferença de 1bp
- `calculo_hedge_di()`: Hedge simples (quantidade/100)

**Dependências de Dados**:
- CDI para carregamento
- DI para hedge

**Exemplo de Uso**:
```python
ltn = LTN("2025-01-01", taxa=12.5)
ltn.quantidade = 50000
print(f"PU D0: {ltn.pu_d0:.6f}")
print(f"Carrego BRL: {ltn.carrego_brl:.2f}")
print(f"Hedge DI: {ltn.hedge_di}")
```

#### LFT (Letras Financeiras do Tesouro)

**Características**:
- Pós-fixado (Selic)
- Zero cupom
- Requer VNA LFT

**Cálculos Específicos**:
- `calculo_vna_ajustado_lft()`: VNA ajustado pela Selic
- `pu_cotcao_lft()`: Cotação baseada em taxa
- `taxa_pu_lft()`: PU considerando VNA e cotação

**Dependências de Dados**:
- VNA LFT (scraping)
- CDI para carregamento

**Exemplo de Uso**:
```python
lft = LFT("2025-01-01", taxa=12.5)
lft.financeiro = 75000
print(f"PU D0: {lft.pu_d0:.6f}")
print(f"PU Termo: {lft.pu_termo:.6f}")
```

#### NTNF (Notas do Tesouro Nacional - Série F)

**Características**:
- Prefixado
- Cupom semestral (10% a.a.)
- Similar a NTNB mas sem indexação IPCA

**Cálculos Específicos**:
- `cash_flow_ntnf()`: Fluxo de cupons semestrais
- `taxa_pu_ntnf()`: PU baseado em cupons
- `calculo_hedge_di()`: Hedge usando DV01 de DI

**Dependências de Dados**:
- CDI para carregamento
- DI para hedge

**Exemplo de Uso**:
```python
ntnf = NTNF("2025-01-01", taxa=12.5)
ntnf.quantidade = 30000
print(f"PU D0: {ntnf.pu_d0:.6f}")
print(f"DV01: {ntnf.dv01:.2f}")
```

#### DI (Contratos de Depósito Interbancário)

**Características**:
- Pós-fixado (CDI)
- Zero cupom
- Identificado por código (ex: "DI1F27")

**Cálculos Específicos**:
- `taxa_pu_di()`: PU do contrato DI
- `calculo_dv01_di()`: DV01 do contrato

**Dependências de Dados**:
- BMF para ajustes

**Exemplo de Uso**:
```python
di = DI(codigo="DI1F27", taxa=13.5)
di.quantidade = 1000
print(f"PU: {di.pu:.6f}")
print(f"DV01: {di.dv01:.2f}")
```

### 4.2. Dados - Sistema de Dados de Mercado

#### VariaveisMercado (Orquestrador)

**Localização**: `dados/orquestrador.py`

**Responsabilidades**:
- Orquestrar carregamento de todos os dados de mercado
- Gerenciar cache em memória
- Coordenar fallback (scraping → cache → backup)
- Fornecer interface única para acesso a dados

**Métodos Principais**:

```python
class VariaveisMercado:
    def get_feriados(force_update=False) -> List
    def get_cdi(force_update=False) -> float
    def get_ipca_dict(data=None, force_update=False) -> Dict
    def get_vna_lft(data=None, force_update=False) -> Dict
    def get_anbimas(data=None, force_update=False) -> Dict[str, DataFrame]
    def get_bmf(data=None, force_update=False) -> Dict[str, DataFrame]
    def atualizar_tudo(verbose=True) -> None
    def limpar_cache() -> None
```

**Estratégia de Carregamento**:

1. **Cache em memória**: Se já carregado e `force_update=False`, retorna cache
2. **Cache em disco**: Tenta carregar de arquivo pickle
3. **Scraping**: Faz scraping da fonte original
4. **Backup**: Em caso de falha, usa arquivo Excel de backup
5. **Salva cache**: Após sucesso, salva em pickle

**Exemplo de Uso**:
```python
vm = VariaveisMercado()
feriados = vm.get_feriados()
cdi = vm.get_cdi()
anbimas = vm.get_anbimas()  # Retorna dict com DataFrames por tipo
```

#### Processamento de Dados

**anbimas.py**: Processa dados brutos da ANBIMA
- Limpa e estrutura dados
- Separa por tipo de título
- Converte formatos de data e número

**bmf.py**: Processa dados da BMF
- `ajustes_bmf()`: Processa dados do UpToData
- `ajustes_bmf_net()`: Processa dados alternativos
- Separa contratos DI e DAP

**ipca.py**: Processa dados de IPCA
- `dicionario_ipca()`: Cria dicionário com índices IPCA
- `inicio_fim_mes_ipca()`: Calcula período do mês IPCA
- Determina qual IPCA usar (fechado vs projeção)

#### Sistema de Cache

**Localização**: `dados/cache.py`

**Funcionalidades**:
- `save_cache(data, filename)`: Salva objeto em pickle
- `load_cache(filename)`: Carrega objeto de pickle
- `clear_cache(filename)`: Remove arquivo de cache

**Localização**: `dados/cache_data/`

**Arquivos de Cache**:
- `feriados.pkl`
- `cdi.pkl`
- `ipca_dict.pkl`
- `anbimas.pkl`
- `bmf.pkl`
- `vna_lft.pkl`

#### Sistema de Backup

**Localização**: `dados/backup.py`

**Funcionalidades**:
- `backup_cdi()`: Carrega CDI de Excel
- `backup_feriados()`: Carrega feriados de Excel
- `backup_ipca_fechado()`: Carrega IPCA fechado de Excel
- `backup_ipca_proj()`: Carrega projeção IPCA de Excel
- `backup_anbimas()`: Carrega dados ANBIMA de Excel
- `backup_bmf()`: Carrega dados BMF de Excel

**Localização**: `dados/backup_excel/`

**Arquivos de Backup**:
- `cdi.xlsx`
- `feriados.xlsx`
- `ipca_fechado.xlsx`
- `ipca_proj.xlsx`
- `anbimas.xlsx`
- `bmf.xlsx`

### 4.3. Scraping - Coleta de Dados

#### anbima_scraping.py

**Funções**:
- `scrap_cdi()`: Coleta taxa CDI
- `scrap_feriados()`: Coleta lista de feriados
- `scrap_proj_ipca()`: Coleta projeção de IPCA
- `scrap_anbimas(data)`: Coleta dados de todos os títulos ANBIMA
- `scrap_vna_lft(data)`: Coleta VNA LFT

**Fonte**: Site da ANBIMA

#### sidra_scraping.py

**Funções**:
- `puxar_valores_ipca_fechado()`: Coleta IPCA fechado do IBGE/SIDRA

**Fonte**: API SIDRA/IBGE

#### uptodata_scraping.py

**Funções**:
- `scrap_ajustes_bmf(data)`: Coleta ajustes de contratos BMF
- `definir_caminho_adj_bmf()`: Define caminho para dados

**Fonte**: UpToData

#### bmf_net_scraping.py

**Funções**:
- `scrap_bmf_net()`: Coleta dados BMF alternativos

**Fonte**: Site BMF

### 4.4. Utils - Utilitários

#### datas.py

**Funções Principais**:

- `adicionar_dias_uteis(data, n_dias, feriados)`: Adiciona n dias úteis
- `e_dia_util(data, feriados)`: Verifica se é dia útil
- `dias_trabalho_total(data_inicio, data_fim, feriados)`: Conta dias úteis entre datas
- `listar_dias_entre_datas(data_liquidacao, datas, feriados)`: Lista dias úteis para cada data
- `ajustar_para_proximo_dia_util(datas, feriados)`: Ajusta datas para próximo dia útil
- `data_vencimento_ajustada(data, feriados)`: Ajusta data de vencimento
- `datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia, feriados)`: Gera datas de cupons

**Características**:
- Todas as funções consideram feriados
- Usam pandas para manipulação de datas
- Suportam carregamento lazy de feriados

#### paths.py

**Funções**:
- `path_backup_csv()`: Caminho para backup CSV
- `path_backup_pickle()`: Caminho para backup pickle
- `path_logs()`: Caminho para logs

#### carregamento_var_globais.py

**Funções de Carregamento Lazy**:

- `_carregar_feriados_se_necessario(feriados)`: Carrega feriados se None
- `_carrecar_ipca_dict_se_necessario(ipca_dict)`: Carrega IPCA se None
- `_carrecar_cdi_se_necessario(cdi)`: Carrega CDI se None
- `_carregar_vna_lft_se_necessario(vna_lft)`: Carrega VNA LFT se None

**Padrão**: Todas criam instância de `VariaveisMercado` se necessário

---

## Detalhamento por Tipo de Título

### NTNB - Fluxo de Cálculo

```
1. Inicialização
   ├── Carrega IPCA dict
   ├── Carrega feriados
   ├── Carrega CDI
   └── Busca taxa ANBIMA

2. Configuração DAP
   ├── Calcula código DAP (vencimento_codigo_bmf)
   ├── Busca ajuste DAP da BMF
   └── Calcula prêmio ANBIMA-DAP

3. Configuração Taxa
   ├── Se taxa não fornecida:
   │   ├── Se premio fornecido: taxa = ajuste_dap + premio/100
   │   └── Senão: taxa = taxa_anbima
   └── Se taxa fornecida: usa taxa fornecida

4. Cálculo Principal (_calcular)
   ├── Calcula VNA ajustado (calculo_vna_ajustado_ntnb)
   ├── Calcula cash flow (cash_flow_ntnb)
   │   ├── Gera datas de cupons
   │   ├── Calcula valores futuros (FV)
   │   └── Calcula valores presentes (PV)
   ├── Calcula PU D0 e PU Termo
   ├── Calcula Duration
   ├── Calcula DV01
   ├── Calcula PU Carregado (com CDI)
   ├── Calcula PU Ajustado (com IPCA)
   └── Calcula Carregamento

5. Cálculo Hedge DAP
   └── hedge_dap = dv01_titulo / dv01_dap
```

### LTN - Fluxo de Cálculo

```
1. Inicialização
   ├── Carrega feriados
   ├── Carrega CDI
   └── Busca taxa ANBIMA

2. Configuração DI
   ├── Calcula código DI (vencimento_codigo_bmf)
   ├── Busca ajuste DI da BMF
   └── Calcula prêmio ANBIMA-DI

3. Configuração Taxa
   ├── Se taxa não fornecida:
   │   ├── Se premio e DI fornecidos: taxa = di + premio/100
   │   └── Senão: taxa = taxa_anbima
   └── Se taxa fornecida: usa taxa fornecida

4. Cálculo Principal (_calcular)
   ├── Calcula PU D0 (taxa_pu_ltn)
   ├── Calcula PU Termo
   ├── Calcula DV01 (diferença de 1bp)
   ├── Calcula PU Carregado (com CDI)
   └── Calcula Carregamento

5. Cálculo Hedge DI
   └── hedge_di = quantidade / 100 (regra simples)
```

### LFT - Fluxo de Cálculo

```
1. Inicialização
   ├── Carrega feriados
   ├── Carrega CDI
   └── Busca taxa ANBIMA

2. Configuração Taxa
   └── taxa = taxa fornecida ou taxa_anbima

3. Cálculo Principal (_calcular)
   ├── Calcula cotação (pu_cotcao_lft)
   ├── Calcula VNA ajustado (calculo_vna_ajustado_lft)
   ├── Calcula PU D0 (taxa_pu_lft)
   ├── Calcula PU Termo
   └── Calcula PU Carregado (com CDI)
```

### NTNF - Fluxo de Cálculo

```
1. Inicialização
   ├── Carrega feriados
   ├── Carrega CDI
   └── Busca taxa ANBIMA

2. Configuração DI
   ├── Calcula código DI
   ├── Busca ajuste DI da BMF
   └── Calcula prêmio ANBIMA-DI

3. Configuração Taxa
   ├── Se taxa não fornecida:
   │   ├── Se premio e DI fornecidos: taxa = di + premio/100
   │   └── Senão: taxa = taxa_anbima
   └── Se taxa fornecida: usa taxa fornecida

4. Cálculo Principal (_calcular)
   ├── Calcula PU D0 (taxa_pu_ntnf)
   │   ├── Gera datas de cupons
   │   ├── Calcula valores futuros (FV)
   │   └── Calcula cotação
   ├── Calcula PU Termo
   ├── Calcula DV01 (diferença de 1bp)
   ├── Calcula PU Carregado (com CDI)
   └── Calcula Carregamento

5. Cálculo Hedge DI
   └── hedge_di = dv01_titulo / dv01_di
```

---

## Padrões e Convenções

### Convenções de Nomenclatura

- **Classes**: PascalCase (ex: `NTNB`, `VariaveisMercado`)
- **Funções**: snake_case (ex: `calculo_ntnb`, `adicionar_dias_uteis`)
- **Atributos privados**: Prefixo `_` (ex: `_taxa`, `_quantidade`)
- **Propriedades públicas**: Sem prefixo (ex: `taxa`, `quantidade`)

### Padrões de Código

1. **Inicialização de Títulos**:
   - Sempre aceita `variaveis_mercado` opcional
   - Cria instância se não fornecida
   - Carrega dados com fallback

2. **Propriedades Mutáveis**:
   - Setters sempre recalculam valores derivados
   - Validação de valores (ex: quantidade > 0)
   - Atualização consistente de valores relacionados

3. **Cálculos**:
   - Funções puras quando possível
   - Truncamento para precisão (6 casas decimais para PU, 4 para cotação)
   - Uso de dias úteis (252 dias/ano)

4. **Tratamento de Erros**:
   - Validação de vencimentos existentes
   - Mensagens de erro descritivas
   - Fallback para backups em caso de falha

### Truncamento

Padrão usado em todo o módulo:
```python
truncar = lambda valor, casas_decimais: trunc(valor * 10 ** casas_decimais) / 10 ** casas_decimais
```

- PU: 6 casas decimais
- Cotação: 4 casas decimais
- Taxa: 4 casas decimais

---

## Dependências e Integrações

### Dependências Externas

- **pandas**: Manipulação de datas e DataFrames
- **numpy**: Cálculos numéricos e arrays
- **openpyxl**: Leitura de arquivos Excel (backup)
- **requests/beautifulsoup**: Web scraping (implícito)

### Dependências Internas

```
titulospub/
├── core/
│   ├── depende de → dados/orquestrador.py
│   ├── depende de → utils/datas.py
│   └── depende de → utils/carregamento_var_globais.py
├── dados/
│   ├── depende de → scraping/*.py
│   ├── depende de → utils/datas.py
│   └── depende de → dados/cache.py
└── scraping/
    └── depende de → utils/datas.py (alguns)
```

### Fluxo de Dependências

```
Classes de Título
    ↓
VariaveisMercado (orquestrador)
    ↓
├──→ Scraping (fonte primária)
├──→ Cache (otimização)
└──→ Backup (fallback)
```

---

## Pontos de Atenção para Refatoração

### 1. Separação de Domínio e Dados

**Problema Atual**:
- Classes de título dependem diretamente de `VariaveisMercado`
- Acesso direto a dados de mercado dentro das classes
- Difícil testar sem dados reais

**Solução Proposta**:
- Criar interface `MarketDataRepository`
- Classes de título dependem de interface, não implementação
- Injeção de dependência explícita

### 2. Código Duplicado

**Problemas Identificados**:

1. **`_configurar_datas()`**: Idêntico em NTNB, LTN, NTNF
   - **Solução**: Mover para classe base ou helper

2. **`_ajustar_valores_para_quantidade()`**: Código duplicado
   - **Solução**: Mover para classe base

3. **`_ajustar_valores_para_financeiro()`**: Código duplicado
   - **Solução**: Mover para classe base

4. **`calculo_carrego_*()`**: Funções idênticas em LTN e NTNF
   - **Solução**: Função generalizada `calcular_carrego()`

5. **Padrão de cálculo DV01**: Similar em todos (PU com taxa vs taxa+0.01)
   - **Solução**: Função generalizada `calcular_dv01()`

### 3. Acoplamento Forte

**Problemas**:
- Classes de título conhecem detalhes de `VariaveisMercado`
- Funções de cálculo conhecem detalhes de carregamento de dados
- Difícil substituir fonte de dados

**Solução**:
- Abstrações (interfaces)
- Injeção de dependência
- Separação de responsabilidades

### 4. Estado Global Implícito

**Problemas**:
- `VariaveisMercado` mantém estado em memória
- Carregamento lazy pode causar efeitos colaterais
- Difícil rastrear origem dos dados

**Solução**:
- Estado explícito
- Imutabilidade quando possível
- Rastreamento de origem dos dados

### 5. Tratamento de Erros

**Problemas**:
- Falhas silenciosas em alguns casos
- Mensagens de erro inconsistentes
- Falta de logging estruturado

**Solução**:
- Exceções específicas por tipo de erro
- Logging estruturado
- Tratamento de erros consistente

### 6. Testabilidade

**Problemas**:
- Difícil mockar `VariaveisMercado`
- Dependências de scraping em testes
- Dados de teste não isolados

**Solução**:
- Interfaces para mock
- Fixtures de dados de teste
- Testes unitários isolados

### 7. Documentação

**Problemas**:
- Algumas funções sem docstrings
- Falta documentação de fórmulas financeiras
- Falta exemplos de uso

**Solução**:
- Docstrings completas
- Documentação de fórmulas
- Exemplos de uso

### 8. Performance

**Problemas**:
- Recálculo completo em mudanças pequenas
- Cache pode ficar desatualizado
- Scraping pode ser lento

**Solução**:
- Cálculos incrementais quando possível
- Invalidação de cache inteligente
- Scraping assíncrono (futuro)

---

## Exemplos de Uso Completos

### Exemplo 1: Criar NTNB e Calcular Métricas

```python
from titulospub import NTNB

# Criar título
ntnb = NTNB("2035-05-15", taxa=7.53)

# Definir posição por valor financeiro
ntnb.financeiro = 100000

# Acessar métricas
print(f"Quantidade: {ntnb.quantidade:,.0f}")
print(f"PU Termo: {ntnb.pu_termo:.6f}")
print(f"DV01: {ntnb.dv01:.2f}")
print(f"Duration: {ntnb.duration:.4f}")
print(f"Carrego BRL: {ntnb.carrego_brl:.2f}")
print(f"Carrego bps: {ntnb.carrego_bps:.2f}")
print(f"Hedge DAP: {ntnb.hedge_dap}")

# Alterar taxa e recalcular
ntnb.taxa = 7.60
print(f"Novo PU: {ntnb.pu_termo:.6f}")
```

### Exemplo 2: Comparar Títulos (Equivalência)

```python
from titulospub import equivalencia

# Equivalência por DV01
eq_dv01 = equivalencia(
    titulo1="NTNB",
    venc1="2035-05-15",
    titulo2="LTN",
    venc2="2025-01-01",
    qtd1=10000,
    criterio="dv"
)

# Equivalência por Financeiro
eq_fin = equivalencia(
    titulo1="LTN",
    venc1="2025-01-01",
    titulo2="NTNF",
    venc2="2025-07-01",
    qtd1=50000,
    criterio="fin"
)

print(f"Equivalência DV01: {eq_dv01:,.0f}")
print(f"Equivalência Financeiro: {eq_fin:,.0f}")
```

### Exemplo 3: Usar VariaveisMercado Diretamente

```python
from titulospub import VariaveisMercado

vm = VariaveisMercado()

# Carregar dados
feriados = vm.get_feriados()
cdi = vm.get_cdi()
anbimas = vm.get_anbimas()
bmf = vm.get_bmf()

# Forçar atualização
vm.atualizar_tudo(verbose=True)

# Limpar cache
vm.limpar_cache()
```

### Exemplo 4: Compartilhar VariaveisMercado Entre Títulos

```python
from titulospub import NTNB, LTN, VariaveisMercado

# Criar uma instância compartilhada
vm = VariaveisMercado()

# Criar múltiplos títulos usando a mesma instância
ntnb = NTNB("2035-05-15", taxa=7.53, variaveis_mercado=vm)
ltn = LTN("2025-01-01", taxa=12.5, variaveis_mercado=vm)

# Dados são carregados uma vez e reutilizados
```

---

## Guia Rápido de Referência

### Mapeamento de Arquivos Principais

| Componente | Arquivo | Responsabilidade |
|------------|---------|------------------|
| **NTNB** | `core/ntnb/titulo_ntnb.py` | Classe principal NTNB |
| **LTN** | `core/ltn/titulo_ltn.py` | Classe principal LTN |
| **LFT** | `core/lft/titulo_lft.py` | Classe principal LFT |
| **NTNF** | `core/ntnf/titulo_ntnf.py` | Classe principal NTNF |
| **DI** | `core/di/di_contrato.py` | Classe principal DI |
| **Orquestrador** | `dados/orquestrador.py` | VariaveisMercado - gerencia todos os dados |
| **Cache** | `dados/cache.py` | Sistema de cache (pickle) |
| **Backup** | `dados/backup.py` | Funções de backup (Excel) |
| **ANBIMA** | `scraping/anbima_scraping.py` | Scraping ANBIMA |
| **IPCA** | `scraping/sidra_scraping.py` | Scraping IPCA |
| **BMF** | `scraping/uptodata_scraping.py` | Scraping BMF |
| **Datas** | `utils/datas.py` | Funções de manipulação de datas |

### Propriedades Comuns dos Títulos

| Propriedade | Tipo | Descrição | Mutável |
|-------------|------|-----------|---------|
| `taxa` | float | Taxa de juros (%) | Sim |
| `quantidade` | float | Quantidade de títulos | Sim |
| `financeiro` | float | Valor financeiro (R$) | Sim |
| `data_base` | Timestamp | Data base para cálculos | Sim |
| `data_liquidacao` | Timestamp | Data de liquidação | Sim |
| `dias_liquidacao` | int | Dias para liquidação | Sim |
| `pu_d0` | float | Preço unitário à vista | Não |
| `pu_termo` | float | Preço unitário a termo | Não |
| `pu_carregado` | float | Preço unitário carregado | Não |
| `dv01` | float | Sensibilidade a 1bp | Não |
| `carrego_brl` | float | Carregamento em R$ | Não |
| `carrego_bps` | float | Carregamento em pontos base | Não |

### Métodos de Cálculo por Título

| Título | Cálculos Específicos | Dependências Especiais |
|--------|---------------------|------------------------|
| **NTNB** | VNA ajustado, Duration, Hedge DAP | IPCA, DAP |
| **LTN** | PU/Taxa conversão, Hedge DI simples | CDI, DI |
| **LFT** | VNA ajustado LFT, Cotação | VNA LFT, CDI |
| **NTNF** | Cash flow cupons, Hedge DI | CDI, DI |
| **DI** | PU DI, DV01 DI | BMF |

### Estratégia de Carregamento de Dados

```
1. Cache em Memória (VariaveisMercado)
   ↓ (não encontrado)
2. Cache em Disco (pickle)
   ↓ (não encontrado)
3. Scraping (fonte original)
   ↓ (falha)
4. Backup (Excel)
   ↓
5. Salva em Cache (pickle)
```

### Funções de Cálculo Duplicadas

| Função Duplicada | Onde Está | Onde Deveria Estar |
|------------------|-----------|-------------------|
| `_configurar_datas()` | NTNB, LTN, NTNF | Classe base ou helper |
| `_ajustar_valores_para_quantidade()` | NTNB, LTN, NTNF | Classe base |
| `_ajustar_valores_para_financeiro()` | NTNB, LTN, NTNF | Classe base |
| `calculo_carrego_*()` | LTN, NTNF | Função generalizada |
| Padrão DV01 | Todos | Função generalizada |

### Dependências de Dados por Título

| Título | Feriados | CDI | IPCA | ANBIMA | BMF | VNA LFT |
|--------|----------|-----|------|--------|-----|---------|
| **NTNB** | ✅ | ✅ | ✅ | ✅ | ✅ (DAP) | ❌ |
| **LTN** | ✅ | ✅ | ❌ | ✅ | ✅ (DI) | ❌ |
| **LFT** | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **NTNF** | ✅ | ✅ | ❌ | ✅ | ✅ (DI) | ❌ |
| **DI** | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |

### Checklist para Refatoração

- [ ] Criar interface `MarketDataRepository`
- [ ] Criar classe base `TituloBase` com métodos comuns
- [ ] Generalizar `_configurar_datas()` em helper
- [ ] Generalizar `calcular_carrego()` 
- [ ] Generalizar padrão de cálculo DV01
- [ ] Mover `_ajustar_valores_*` para classe base
- [ ] Adicionar injeção de dependência explícita
- [ ] Criar testes unitários com mocks
- [ ] Documentar fórmulas financeiras
- [ ] Adicionar logging estruturado

---

## Conclusão

O módulo `titulospub` é um sistema robusto para cálculo de títulos públicos brasileiros, com:

- **5 tipos de títulos** suportados
- **Sistema completo de dados** com cache e backup
- **Cálculos financeiros precisos** seguindo padrões de mercado
- **Flexibilidade** para trabalhar com quantidade ou valor financeiro

**Principais Oportunidades de Refatoração**:

1. Separar domínio de dados através de interfaces
2. Eliminar código duplicado com classes base e funções generalizadas
3. Melhorar testabilidade com injeção de dependência
4. Documentar fórmulas e decisões de negócio
5. Adicionar logging e tratamento de erros estruturado

Este documento serve como base para entender o funcionamento completo do módulo e planejar refatorações que mantenham a funcionalidade enquanto melhoram a arquitetura e manutenibilidade.

---

## Informações Adicionais

### Versão do Documento
- **Data**: 2026-02-06
- **Versão do Módulo**: 1.0.0
- **Autor**: Documentação gerada para refatoração

### Contato e Suporte
Para questões sobre este documento ou o módulo `titulospub`, consulte:
- Código fonte em `titulospub/`
- Exemplos de uso nas seções acima
- Comentários no código para detalhes de implementação
