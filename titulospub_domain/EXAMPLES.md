# Exemplos de Uso - titulospub_domain

## Exemplo 1: Criar LTN com MarketDataProvider

```python
import pandas as pd
from titulospub_domain import LTN
from titulospub_domain.application.ports.market_data import MarketDataProvider
from titulospub_domain.domain.types import IPCADict

class MeuMarketDataProvider(MarketDataProvider):
    """Implementação exemplo de MarketDataProvider."""
    
    def __init__(self):
        # Em produção, isso viria do banco de dados
        self._feriados = [
            pd.Timestamp('2025-01-01'),
            pd.Timestamp('2025-04-18'),
            pd.Timestamp('2025-05-01'),
        ]
        self._cdi = 13.65
        self._anbimas = {
            ('LTN', pd.Timestamp('2025-01-01')): 12.5,
        }
        self._bmf_ajustes = {
            ('DI', 'DI1F27'): 13.0,
        }
    
    def get_feriados(self):
        return self._feriados
    
    def get_cdi(self):
        return self._cdi
    
    def get_ipca_dict(self, data=None):
        return IPCADict(
            ultimo_mes_ipca=11,
            indice_ipca_fechado_atual=5000.0,
            indice_ipca_fechado_anterior=4950.0,
            var_ipca_atual=1.0,
            var_ipca_anterior=0.9,
            ipca_proj=4.5,
            ipca_usado=4.5
        )
    
    def get_vna_lft(self, data=None):
        return 10000.0
    
    def get_anbima(self, titulo_type, data_vencimento):
        return self._anbimas.get((titulo_type, data_vencimento), 12.0)
    
    def get_bmf_ajuste(self, tipo, codigo):
        return self._bmf_ajustes.get((tipo, codigo))

# Uso
provider = MeuMarketDataProvider()
ltn = LTN(
    data_vencimento_titulo="2025-01-01",
    taxa=12.5,
    quantidade=50000,
    market_data_provider=provider
)

print(f"PU D0: {ltn.pu_d0:.6f}")
print(f"DV01: {ltn.dv01:.2f}")
print(f"Carrego BRL: {ltn.carrego_brl:.2f}")

# Alterar posição por valor financeiro
ltn.financeiro = 100000
print(f"Nova quantidade: {ltn.quantidade:,.0f}")
```

## Exemplo 2: Usar Dados Explícitos (Sem Provider)

```python
from titulospub_domain import LTN
import pandas as pd

# Dados explícitos (do seu banco/API)
feriados = [
    pd.Timestamp('2025-01-01'),
    pd.Timestamp('2025-04-18'),
]
cdi = 13.65

# Criar título passando dados diretamente
ltn = LTN(
    data_vencimento_titulo="2025-01-01",
    taxa=12.5,  # Taxa explícita (não precisa buscar ANBIMA)
    quantidade=50000,
    feriados=feriados,
    cdi=cdi
)

print(f"PU: {ltn.pu_d0:.6f}")
```

## Exemplo 3: Usar Funções de Cálculo Diretamente

```python
from titulospub_domain.domain.pricing import taxa_pu_ltn
from titulospub_domain.domain.risk import calculo_dv01_ltn
import pandas as pd

# Dados
data_base = pd.Timestamp('2025-01-15')
data_liquidacao = pd.Timestamp('2025-01-16')
data_vencimento = pd.Timestamp('2026-01-01')
taxa = 12.5
feriados = [pd.Timestamp('2025-01-01')]

# Calcular PU diretamente
pu = taxa_pu_ltn(
    data=data_base,
    data_liquidacao=data_liquidacao,
    data_vencimento=data_vencimento,
    taxa=taxa,
    feriados=feriados
)

print(f"PU: {pu:.6f}")

# Calcular DV01 diretamente
dv01 = calculo_dv01_ltn(
    data=data_base,
    data_liquidacao=data_liquidacao,
    data_vencimento=data_vencimento,
    taxa=taxa,
    feriados=feriados
)

print(f"DV01: {dv01:.6f}")
```

## Exemplo 4: Comparar com Código Legado

```python
# Código legado
import titulospub as legacy
ltn_legacy = legacy.LTN("2025-01-01", taxa=12.5)

# Código refatorado
from titulospub_domain import LTN
# ... criar provider com mesmos dados ...
ltn_ref = LTN("2025-01-01", taxa=12.5, market_data_provider=provider)

# Comparar resultados
assert abs(ltn_legacy.pu_d0 - ltn_ref.pu_d0) < 0.0001
assert abs(ltn_legacy.dv01 - ltn_ref.dv01) < 0.01
```

## Notas Importantes

1. **Feriados são obrigatórios**: Sempre forneça lista de feriados ou use MarketDataProvider
2. **CDI necessário para carregamento**: Se não fornecido, alguns cálculos podem falhar
3. **Taxa pode ser explícita**: Não precisa buscar ANBIMA se fornecer taxa diretamente
4. **MarketDataProvider é opcional**: Pode passar todos os dados explicitamente
