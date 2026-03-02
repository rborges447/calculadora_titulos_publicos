# titulospub_domain

Módulo de domínio refatorado para cálculo de títulos públicos brasileiros.

## Características

- ✅ **Domínio Puro**: Apenas lógica de negócio, sem scraping/cache/IO
- ✅ **Comportamento Idêntico**: Mesmas fórmulas e resultados do código legado
- ✅ **Testável**: Fácil criar mocks e testes unitários
- ✅ **Extensível**: Interface clara para injetar dados de mercado

## Estrutura

```
titulospub_domain/
├── domain/              # Lógica de negócio pura
│   ├── dates/          # Manipulação de datas
│   ├── cashflows/      # Fluxos de caixa
│   ├── pricing/        # Precificação (PU, taxa)
│   ├── risk/           # Métricas de risco (DV01, Duration)
│   └── instruments/    # Classes de títulos
├── application/         # Interfaces e serviços
│   └── ports/          # MarketDataProvider
└── tests/              # Testes de regressão
```

## Uso Rápido

```python
from titulospub_domain import LTN
from titulospub_domain.application.ports.market_data import MarketDataProvider

# Implementar provider (busca dados do seu banco/API)
class MeuProvider(MarketDataProvider):
    def get_feriados(self):
        return [...]  # Do seu banco
    
    def get_cdi(self):
        return 13.65  # Do seu banco
    
    # ... outros métodos

# Criar título
provider = MeuProvider()
ltn = LTN("2025-01-01", taxa=12.5, market_data_provider=provider)
ltn.financeiro = 100000
print(f"PU: {ltn.pu_d0:.6f}")
```

## Status

- ✅ Estrutura base completa
- ✅ Módulos de cálculo implementados
- ✅ LTN implementada
- ⏳ LFT, NTNB, NTNF, DI (seguir padrão LTN)

## Documentação

Veja `ARCHITECTURE.md` para detalhes completos da arquitetura.
