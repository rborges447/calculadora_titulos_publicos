# Suposições e Riscos Técnicos

## Suposições Implícitas

### 1. Dados de Mercado Sempre Disponíveis

**Suposição:** O sistema assume que sempre consegue obter dados de mercado, seja via scraping ou backup.

**Implicação:** Se tanto scraping quanto backup falharem, o sistema pode quebrar ou retornar erros.

**Mitigação:** 
- Sistema tenta scraping primeiro
- Se falhar, usa backup (arquivos Excel)
- Se ambos falharem, retorna erro descritivo

**Risco:** Médio - Backup pode estar desatualizado

---

### 2. Formato de Datas Consistente

**Suposição:** 
- Datas sempre em formato YYYY-MM-DD (string) ou pd.Timestamp
- Feriados sempre em formato compatível com pandas

**Implicação:** Datas em formato incorreto podem causar erros de parsing.

**Mitigação:** Validação via Pydantic na API

**Risco:** Baixo - Validação automática

---

### 3. Taxas em Formato Decimal

**Suposição:**
- Taxas sempre em porcentagem (ex: 12.5 = 12.5%)
- Premios sempre em pontos base (ex: 0.5 = 50 bps)

**Implicação:** Confusão entre formato decimal e porcentagem pode causar cálculos incorretos.

**Mitigação:** Documentação clara e validação de ranges

**Risco:** Médio - Requer atenção do desenvolvedor

---

### 4. Vencimentos Válidos

**Suposição:** Vencimentos sempre existem na base ANBIMA.

**Implicação:** Se vencimento não existir, sistema lança ValueError.

**Mitigação:** Endpoint `/vencimentos/{tipo}` lista apenas vencimentos válidos

**Risco:** Baixo - Validação prévia disponível

---

### 5. Estado de Carteiras em Memória

**Suposição:** Carteiras são mantidas em memória e não persistem entre reinicializações.

**Implicação:** 
- Carteiras perdidas se servidor reiniciar
- Com múltiplos workers, cada worker tem seu próprio estado

**Mitigação:** Documentado no código, migração para banco/Redis recomendada

**Risco:** Alto - Perda de dados em produção

---

### 6. Thread-Safety

**Suposição:** Sistema funciona corretamente com 1 worker.

**Implicação:** 
- Com múltiplos workers, cache e carteiras não são compartilhados
- Pode causar inconsistências

**Mitigação:** Por padrão usa 1 worker, múltiplos workers requerem migração

**Risco:** Médio - Limitado a 1 worker por padrão

---

### 7. Cache Sem Expiração Automática

**Suposição:** Cache é válido até ser atualizado manualmente.

**Implicação:** Dados podem ficar desatualizados se não atualizar.

**Mitigação:** API atualiza automaticamente na inicialização (uma vez por dia)

**Risco:** Baixo - Atualização automática diária

---

## Riscos Técnicos

### 1. Scraping Pode Falhar

**Risco:** Sites externos podem estar indisponíveis ou mudar estrutura HTML.

**Impacto:** Alto - Sistema depende de dados externos

**Probabilidade:** Média - Sites podem mudar ou estar offline

**Mitigação:**
- Sistema usa backup quando scraping falha
- Arquivos Excel mantidos como fallback
- Logs de erro para debugging

**Ação Recomendada:**
- Monitorar falhas de scraping
- Atualizar arquivos Excel periodicamente
- Considerar múltiplas fontes de dados

---

### 2. Cache Desatualizado

**Risco:** Cache pode conter dados antigos se não atualizar manualmente.

**Impacto:** Médio - Cálculos podem usar dados desatualizados

**Probabilidade:** Baixa - Atualização automática diária

**Mitigação:**
- Atualização automática na inicialização da API
- Endpoint `/atualizar-mercado` para atualização manual
- Controle de última atualização via arquivo JSON

**Ação Recomendada:**
- Monitorar data da última atualização
- Alertar se dados muito antigos (> 1 dia)

---

### 3. Carteiras em Memória

**Risco:** Carteiras perdidas se servidor reiniciar ou com múltiplos workers.

**Impacto:** Alto - Perda de dados do usuário

**Probabilidade:** Alta - Reinicializações são comuns

**Mitigação:**
- Documentado claramente no código
- Por padrão usa 1 worker
- Carteiras são temporárias

**Ação Recomendada:**
- Migrar para banco de dados ou Redis
- Implementar persistência de carteiras
- Suportar múltiplos workers

---

### 4. Thread-Safety

**Risco:** Cache e carteiras não são thread-safe com múltiplos workers.

**Impacto:** Médio - Inconsistências entre workers

**Probabilidade:** Média - Se usar múltiplos workers

**Mitigação:**
- Por padrão usa 1 worker
- Documentado que múltiplos workers requerem migração

**Ação Recomendada:**
- Migrar cache para Redis ou banco compartilhado
- Migrar carteiras para banco de dados
- Implementar locks se necessário

---

### 5. Dependência de Bibliotecas Externas

**Risco:** Pandas, requests, etc podem ter breaking changes.

**Impacto:** Médio - Pode quebrar funcionalidades

**Probabilidade:** Baixa - Versões fixadas

**Mitigação:**
- Versões fixadas em requirements.txt
- Testes automatizados (quando implementados)

**Ação Recomendada:**
- Manter dependências atualizadas
- Testar atualizações em ambiente de desenvolvimento
- Ter plano de rollback

---

### 6. Performance com Muitos Títulos

**Risco:** Cálculos podem ser lentos com muitos títulos em uma carteira.

**Impacto:** Baixo - Performance geralmente boa

**Probabilidade:** Baixa - Cálculos são eficientes

**Mitigação:**
- Cálculos são puros e rápidos
- Cache reduz necessidade de recalcular

**Ação Recomendada:**
- Monitorar tempo de resposta
- Considerar cache de resultados se necessário
- Otimizar se houver problemas

---

### 7. Validação de Dados

**Risco:** Dados inválidos podem causar erros ou cálculos incorretos.

**Impacto:** Alto - Cálculos financeiros incorretos são críticos

**Probabilidade:** Baixa - Validação via Pydantic

**Mitigação:**
- Validação automática via Pydantic na API
- Validação de ranges (ex: quantidade > 0)
- Mensagens de erro descritivas

**Ação Recomendada:**
- Manter validações atualizadas
- Adicionar testes de validação
- Documentar formatos esperados

---

### 8. Segurança

**Risco:** Sistema não tem autenticação/autorização.

**Impacto:** Alto - Acesso não controlado

**Probabilidade:** Alta - Sistema público

**Mitigação:**
- Nenhuma (sistema atual não tem segurança)

**Ação Recomendada:**
- Implementar autenticação
- Implementar autorização por usuário
- Rate limiting para prevenir abuso
- HTTPS em produção

---

### 9. Logging e Monitoramento

**Risco:** Falhas podem passar despercebidas sem logging adequado.

**Impacto:** Médio - Debugging difícil

**Probabilidade:** Média - Erros podem ocorrer

**Mitigação:**
- Alguns prints no código
- Erros retornados via HTTP

**Ação Recomendada:**
- Implementar logging estruturado
- Monitoramento de erros
- Alertas para falhas críticas
- Métricas de performance

---

### 10. Escalabilidade

**Risco:** Sistema pode não escalar bem com muitos usuários simultâneos.

**Impacto:** Médio - Performance degradada

**Probabilidade:** Média - Depende do uso

**Mitigação:**
- Arquitetura stateless (exceto carteiras)
- Cache reduz carga
- Cálculos são eficientes

**Ação Recomendada:**
- Testes de carga
- Monitoramento de performance
- Otimização se necessário
- Considerar CDN para frontend

---

## Riscos de Negócio

### 1. Cálculos Incorretos

**Risco:** Erros em fórmulas financeiras podem causar perdas financeiras.

**Impacto:** Crítico

**Mitigação:**
- Código revisado
- Fórmulas baseadas em padrões do mercado
- Validação de dados

**Ação Recomendada:**
- Revisão por especialistas financeiros
- Testes com dados conhecidos
- Auditoria periódica de cálculos

---

### 2. Dados de Mercado Incorretos

**Risco:** Dados de mercado incorretos podem causar cálculos incorretos.

**Impacto:** Crítico

**Mitigação:**
- Múltiplas fontes (scraping + backup)
- Validação de dados
- Logs de origem dos dados

**Ação Recomendada:**
- Validação cruzada de dados
- Alertas para dados suspeitos
- Auditoria de fontes

---

## Recomendações Prioritárias

1. **Alta Prioridade:**
   - Migrar carteiras para banco de dados
   - Implementar autenticação/autorização
   - Adicionar logging estruturado

2. **Média Prioridade:**
   - Suportar múltiplos workers
   - Implementar monitoramento
   - Adicionar testes automatizados

3. **Baixa Prioridade:**
   - Otimizações de performance
   - Melhorias de UX
   - Documentação adicional

---

## Conclusão

O sistema atual é funcional e adequado para uso interno ou com poucos usuários. Para produção com muitos usuários, recomenda-se:

1. Migrar estado (carteiras) para persistência externa
2. Implementar segurança (autenticação/autorização)
3. Adicionar monitoramento e alertas
4. Implementar testes automatizados
5. Documentar processos operacionais
