# Calculadora de Títulos Públicos

Sistema completo para cálculo e análise de títulos públicos brasileiros com API FastAPI e interface Dash.

## Arquitetura do Projeto

O projeto segue uma arquitetura em camadas bem definida:

```
calculadora_titulos_publicos/
├── titulospub/            # Camada de Domínio (lógica de negócio)
│   ├── core/             # Classes de títulos e cálculos
│   ├── dados/            # Dados de mercado e cache
│   ├── scraping/         # Coleta de dados externos
│   └── utils/            # Utilitários
├── api/                   # Camada de API (FastAPI)
│   ├── main.py           # Aplicação principal
│   ├── models.py         # Modelos Pydantic
│   └── routers/          # Endpoints por tipo de título
├── dash_app/              # Camada de Frontend (Dash)
│   ├── app.py            # Aplicação Dash
│   ├── pages/            # Páginas da interface
│   ├── components/       # Componentes reutilizáveis
│   └── utils/             # Utilitários do frontend
├── run_api.py            # Script para iniciar API
└── run_dash_app.py       # Script para iniciar Dash
```

**Princípios Arquiteturais:**
- `titulospub/` é completamente independente de frameworks web
- `api/` importa `titulospub/` mas não executa cálculos
- `dash_app/` consome apenas a API via HTTP (não importa `titulospub/`)

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar pacote titulospub em modo desenvolvimento
pip install -e .
```

## Como Usar

### 1. Iniciar a API

```bash
python run_api.py
```

A API estará disponível em: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs
- Documentação alternativa: http://localhost:8000/redoc

**Configuração de Workers:**
- Por padrão, usa 1 worker (adequado para desenvolvimento)
- Para produção com múltiplos workers, configure via variável de ambiente:
  ```bash
  export API_WORKERS=4
  python run_api.py
  ```

### 2. Iniciar Interface Dash

```bash
python run_dash_app.py
```

A interface abrirá automaticamente em: http://127.0.0.1:8050

**Nota:** O Dash consome a API via HTTP, então a API deve estar rodando primeiro.

## Endpoints da API

### Títulos Individuais
- `POST /titulos/ltn` - Criar título LTN
- `POST /titulos/lft` - Criar título LFT
- `POST /titulos/ntnb` - Criar título NTNB
- `POST /titulos/ntnb/hedge-di` - Calcular hedge DI para NTNB
- `POST /titulos/ntnf` - Criar título NTNF

### Carteiras
- `POST /carteiras/{tipo}` - Criar carteira (ltn, lft, ntnb, ntnf)
- `GET /carteiras/{carteira_id}` - Obter dados da carteira
- `PUT /carteiras/{carteira_id}/taxa` - Atualizar taxa de um título
- `PUT /carteiras/{carteira_id}/dias` - Atualizar dias de liquidação

### Outros
- `POST /equivalencia` - Calcular equivalência entre títulos
- `GET /vencimentos/{tipo}` - Listar vencimentos disponíveis
- `GET /health` - Health check da API
- `GET /ready` - Readiness check (para load balancers)
- `GET /live` - Liveness check (para orquestradores)

## Uso do Pacote Python

```python
from titulospub import NTNB, LTN, LFT, NTNF, equivalencia

# Criar título
ltn = LTN("2025-01-01", taxa=12.5)
ltn.quantidade = 50000
print(f"Financeiro: R$ {ltn.financeiro:,.2f}")

# Calcular equivalência
eq = equivalencia("LTN", "2025-01-01", "NTNB", "2035-05-15", 
                  qtd1=10000, criterio="dv")
```


## Testes

O projeto inclui testes de regressão para garantir que mudanças não alterem comportamento:

```bash
# Executar todos os testes
pytest tests/regression/

# Executar com verbose
pytest tests/regression/ -v
```

**Cobertura:** 15 testes cobrindo endpoints principais (LTN, LFT, NTNB, NTNF, equivalência, vencimentos)

## Desenvolvido com

- **FastAPI** - Framework web moderno para API REST
- **Dash** - Framework web para interface interativa
- **Python 3.8+** - Linguagem de programação
- **Pydantic** - Validação de dados
- **Pandas** - Manipulação de dados financeiros
- **pytest** - Framework de testes

## Documentação Adicional

Para mais detalhes sobre o sistema, consulte:
- `DOCS_CODEBASE.md` - Documentação completa do código e arquitetura
- `explain/` - Documentação explicativa detalhada:
  - `00_project_summary.md` - Resumo geral do projeto
  - `01_modules_map.md` - Mapa de módulos
  - `02_execution_flow.md` - Fluxos de execução
  - `03_functions_index.md` - Índice de funções e classes
  - `04_assumptions_and_risks.md` - Suposições e riscos
- `RUNBOOK.md` - Guia de operação e deploy






