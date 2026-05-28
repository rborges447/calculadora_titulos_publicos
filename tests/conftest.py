"""Suite de testes de regressão — Spec 001 (VariaveisMercado).

Esta suite congela o comportamento atual de ``VariaveisMercado`` e dos
consumidores (títulos, API) para detectar regressões antes e depois da
refatoração para lake/pacote de dados.

Fixtures de baseline: ``tests/fixtures/variaveis_mercado/``
Golden files (cálculos/API): ``tests/fixtures/golden/``

Comando principal (após Fase 3+):
    pytest tests/ -m regression -v
"""
