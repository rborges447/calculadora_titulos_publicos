# Testes - Calculadora de Títulos Públicos

Esta suíte de testes "congela" o comportamento atual do sistema, garantindo que refatorações não alterem os resultados dos cálculos.

## Estrutura

```
tests/
├── __init__.py
├── conftest.py              # Configuração do pytest
├── test_titulospub_calculos.py  # Testes de cálculos principais
├── test_api.py              # Testes da API FastAPI
├── test_dash.py             # Smoke tests do Dash
└── README.md                # Este arquivo
```

## Executando os Testes

### Instalar dependências de teste

```bash
pip install pytest pytest-cov
```

### Executar todos os testes

```bash
pytest tests/
```

### Executar testes específicos

```bash
# Apenas testes de cálculos
pytest tests/test_titulospub_calculos.py

# Apenas testes da API
pytest tests/test_api.py

# Apenas testes do Dash
pytest tests/test_dash.py
```

### Executar com cobertura

```bash
pytest tests/ --cov=titulospub --cov=api --cov=dash_app
```

## Objetivo dos Testes

Estes testes têm o objetivo de:

1. **Congelar comportamento atual:** Garantir que refatorações não alterem resultados
2. **Verificar determinismo:** Mesmo input → mesmo output
3. **Detectar estado global:** Múltiplas chamadas devem produzir resultados consistentes
4. **Validar arquitetura:** Dash não importa titulospub, API usa titulospub corretamente

## Notas

- Alguns testes podem ser pulados (`pytest.skip`) se vencimentos não estiverem disponíveis
- Testes de API usam `TestClient` do FastAPI (não requerem servidor rodando)
- Testes do Dash são smoke tests (apenas verificam inicialização e estrutura)
