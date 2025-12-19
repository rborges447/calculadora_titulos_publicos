# Testes de Regressão (Golden Master)

## Objetivo

Garantir que mudanças no código não alterem o comportamento da API, especialmente:
- Estrutura de respostas
- Valores numéricos principais (PU, taxa, DV01, etc.)
- Campos obrigatórios e opcionais
- Formato de datas e números

## Execução

```bash
# Executar todos os testes
pytest tests/regression/

# Executar com verbose
pytest tests/regression/ -v

# Executar um arquivo específico
pytest tests/regression/test_titulos.py

# Executar um teste específico
pytest tests/regression/test_titulos.py::TestLTN::test_criar_ltn_com_taxa
```

## Limitações

1. **Vencimentos de exemplo**: Os vencimentos em `conftest.py` podem precisar ser ajustados conforme dados reais disponíveis no cache/backup.

2. **Cache/Backup**: Os testes assumem que cache ou backup está disponível. Se não estiver, os testes podem falhar ou tentar fazer scraping (não recomendado durante testes).

3. **Valores numéricos**: Os testes validam que valores existem e são positivos, mas não validam valores exatos (que podem variar com dados de mercado).

## Adicionar Novos Testes

Ao adicionar novos testes:
1. Use fixtures de `conftest.py` quando possível
2. Valide estrutura de resposta (campos obrigatórios)
3. Valide tipos de dados
4. Valide valores numéricos principais (mas não valores exatos)
5. Documente limitações específicas do teste

## Manutenção

- Se um teste falhar após mudança, **NÃO** atualize o teste sem investigar
- Se a mudança foi intencional e correta, atualize o teste
- Se a mudança foi acidental, **REVERTA** a mudança no código
