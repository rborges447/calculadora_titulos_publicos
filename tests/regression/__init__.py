"""
Testes de regressão (Golden Master) para garantir que mudanças não alterem comportamento.

Estes testes validam:
- Estrutura de respostas da API
- Valores numéricos principais (PU, taxa, DV01, etc.)
- Campos obrigatórios e opcionais
- Formato de datas e números

IMPORTANTE: Estes testes usam cache/backup existente para evitar scraping durante testes.
"""
