# Arquitetura do Módulo titulospub_domain

## Visão Geral

O módulo `titulospub_domain` é uma refatoração do módulo legado `titulospub`, focada **exclusivamente no domínio** (lógica de negócio e cálculos financeiros), removendo todas as dependências de infraestrutura (scraping, cache, IO, banco de dados).

## Princípios de Design

1. **Separação de Domínio e Infraestrutura**: O domínio não conhece detalhes de como os dados são obtidos
2. **Dependências Explícitas**: Todos os dados necessários são passados como parâmetros ou via interfaces
3. **Comportamento Idêntico**: Para as mesmas entradas, produz os mesmos resultados do código legado
4. **Testabilidade**: Fácil criar mocks e testes unitários isolados

## Estrutura do Módulo

```
titulospub_domain/
├── __init__.py                 # Facade principal - reexporta classes públicas
├── domain/                     # Lógica de negócio pura
│   ├── __init__.py
│   ├── types.py               # Tipos e estruturas de dados
│   ├── conventions.py         # Convenções financeiras e constantes
│   ├── auxilio.py             # Funções auxiliares (códigos BMF, etc)
│   ├── dates/                 # Manipulação de datas e calendários
│   │   ├── calendar.py       # Funções de calendário (dias úteis, etc)
│   │   └── schedule.py       # Geração de cronogramas (cupons, etc)
│   ├── cashflows/            # Cálculo de fluxos de caixa
│   │   ├── cashflow.py       # Fluxos de caixa (NTNB, NTNF)
│   │   └── indexing.py       # Indexação (VNA, IPCA, LFT)
│   ├── pricing/              # Precificação
│   │   ├── price_yield.py    # Conversões PU <-> taxa
│   │   └── calculations.py  # Cálculos consolidados por título
│   ├── risk/                 # Métricas de risco
│   │   ├── dv01.py          # Cálculo de DV01
│   │   ├── duration.py      # Cálculo de Duration
│   │   └── equivalence.py   # Equivalência entre títulos
│   └── instruments/          # Classes de títulos
│       ├── base.py           # Classe base abstrata
│       ├── ltn.py            # LTN
│       ├── lft.py            # LFT (a implementar)
│       ├── ntnb.py           # NTNB (a implementar)
│       ├── ntnf.py           # NTNF (a implementar)
│       └── di.py             # DI (a implementar)
├── application/               # Camada de aplicação (opcional)
│   ├── ports/               # Interfaces (ports)
│   │   └── market_data.py  # Interface MarketDataProvider
│   └── services/            # Serviços de aplicação (opcional)
└── tests/                    # Testes
    └── test_equivalence_vs_legacy.py  # Testes de regressão
```

## O Que Foi Removido

- **Scraping**: Todas as funções de web scraping foram removidas
- **Cache**: Sistema de cache (pickle) foi removido
- **Backup**: Funções de backup (Excel) foram removidas
- **VariaveisMercado**: Classe orquestradora foi substituída por interface `MarketDataProvider`
- **Carregamento Automático**: Funções que carregavam dados automaticamente foram removidas

## O Que Foi Mantido

- **Todas as fórmulas financeiras**: Cálculos de PU, DV01, Duration, etc. permanecem idênticos
- **Convenções**: Truncamento, precisão, contagem de dias úteis, etc.
- **API Pública**: Classes principais (LTN, LFT, NTNB, NTNF, DI) mantêm interface similar
- **Lógica de Negócio**: Toda a lógica de cálculo e regras de negócio

## Como Injetar Dados

### Opção 1: Via MarketDataProvider (Recomendado)

Crie uma implementação da interface `MarketDataProvider` que busca dados do seu banco/API:

```python
from titulospub_domain.application.ports.market_data import MarketDataProvider
from titulospub_domain import LTN

class MeuMarketDataProvider(MarketDataProvider):
    def get_feriados(self):
        # Busca do banco de dados
        return db.query("SELECT data FROM feriados")
    
    def get_cdi(self):
        return db.query("SELECT taxa FROM cdi WHERE data = hoje()")
    
    # ... outros métodos

# Uso
provider = MeuMarketDataProvider()
ltn = LTN("2025-01-01", market_data_provider=provider)
```

### Opção 2: Parâmetros Explícitos

Passe todos os dados necessários diretamente:

```python
from titulospub_domain import LTN

feriados = [...]  # Do seu banco
cdi = 13.65  # Do seu banco

ltn = LTN(
    data_vencimento_titulo="2025-01-01",
    taxa=12.5,
    feriados=feriados,
    cdi=cdi
)
```

## Exemplo de Uso

```python
from titulospub_domain import LTN, NTNB
from titulospub_domain.application.ports.market_data import MarketDataProvider

# Implementar provider (exemplo simplificado)
class MeuProvider(MarketDataProvider):
    def get_feriados(self):
        return [pd.Timestamp('2025-01-01'), ...]
    
    def get_cdi(self):
        return 13.65
    
    # ... outros métodos

# Criar títulos
provider = MeuProvider()

ltn = LTN("2025-01-01", taxa=12.5, market_data_provider=provider)
ltn.financeiro = 100000
print(f"Quantidade: {ltn.quantidade:,.0f}")
print(f"PU: {ltn.pu_d0:.6f}")
print(f"DV01: {ltn.dv01:.2f}")
```

## Testes

Os testes em `tests/test_equivalence_vs_legacy.py` comparam resultados do código refatorado com o legado para garantir equivalência.

Execute com:
```bash
pytest titulospub_domain/tests/test_equivalence_vs_legacy.py -v
```

## Migração do Código Legado

Para migrar código que usa `titulospub`:

1. **Substitua imports**:
   ```python
   # Antes
   from titulospub import LTN
   
   # Depois
   from titulospub_domain import LTN
   ```

2. **Adicione MarketDataProvider** ou passe dados explicitamente:
   ```python
   # Antes
   ltn = LTN("2025-01-01")
   
   # Depois (com provider)
   ltn = LTN("2025-01-01", market_data_provider=meu_provider)
   
   # Ou (dados explícitos)
   ltn = LTN("2025-01-01", feriados=feriados, cdi=cdi, taxa=12.5)
   ```

3. **API permanece compatível**: Propriedades e métodos principais funcionam da mesma forma

## Status de Implementação

- ✅ Estrutura base criada
- ✅ Módulos de datas, cashflows, pricing, risk implementados
- ✅ Classe base de instrumentos criada
- ✅ LTN implementada (parcialmente)
- ⏳ LFT, NTNB, NTNF, DI (a implementar seguindo mesmo padrão)
- ✅ Testes básicos criados
- ✅ Documentação de arquitetura

## Próximos Passos

1. Completar implementação das classes LFT, NTNB, NTNF, DI
2. Expandir testes de regressão
3. Criar adaptador que implementa MarketDataProvider usando código legado (para migração gradual)
4. Adicionar mais exemplos de uso

## Notas Importantes

- **Não altere fórmulas**: Qualquer mudança em fórmulas financeiras deve ser discutida e testada
- **Mantenha precisão**: Truncamentos e arredondamentos devem ser idênticos ao legado
- **Teste antes de usar**: Sempre execute testes de regressão após mudanças
