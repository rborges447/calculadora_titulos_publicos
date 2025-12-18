# Fluxo de Execução do Sistema

## 1. Inicialização da API

```
run_api.py
  └─> uvicorn.run("api.main:app")
       └─> api/main.py: app = FastAPI(...)
            ├─> lifespan() [startup]
            │    ├─> precisa_atualizar_mercado()?
            │    │    └─> Verifica arquivo .ultima_atualizacao.json
            │    ├─> Se sim:
            │    │    ├─> VariaveisMercado()
            │    │    │    └─> Inicializa cache vazio
            │    │    ├─> vm.atualizar_tudo(verbose=True)
            │    │    │    ├─> get_feriados()
            │    │    │    │    ├─> Tentar scraping: scrap_feriados()
            │    │    │    │    │    └─> Requisição HTTP para ANBIMA
            │    │    │    │    ├─> Se falhar: backup_feriados()
            │    │    │    │    │    └─> Ler arquivo Excel
            │    │    │    │    └─> save_cache(feriados, "feriados.pkl")
            │    │    │    ├─> get_ipca_dict()
            │    │    │    │    ├─> Tentar scraping: puxar_valores_ipca_fechado()
            │    │    │    │    │    └─> Requisição HTTP para SIDRA
            │    │    │    │    ├─> Tentar scraping: scrap_proj_ipca()
            │    │    │    │    │    └─> Requisição HTTP para ANBIMA
            │    │    │    │    ├─> Se falhar: backup_ipca_fechado() + backup_ipca_proj()
            │    │    │    │    └─> dicionario_ipca() → save_cache()
            │    │    │    ├─> get_cdi()
            │    │    │    │    ├─> Tentar scraping: scrap_cdi()
            │    │    │    │    ├─> Se falhar: backup_cdi()
            │    │    │    │    └─> save_cache()
            │    │    │    ├─> get_vna_lft()
            │    │    │    ├─> get_anbimas()
            │    │    │    └─> get_bmf()
            │    │    └─> marcar_atualizado()
            │    │         └─> Escrever .ultima_atualizacao.json
            │    └─> Se não: Usar dados em cache
            ├─> app.add_middleware(CORSMiddleware)
            └─> app.include_router(...) [registra todos routers]
                 └─> Servidor uvicorn iniciado na porta 8000
```

## 2. Requisição de Cálculo de Título (Exemplo: LTN)

```
Cliente HTTP
  └─> POST /titulos/ltn
       {
         "data_vencimento": "2025-01-01",
         "taxa": 12.5,
         "quantidade": 50000
       }
       
api/routers/ltn.py: criar_ltn(request)
  ├─> Validação Pydantic: LTNRequest(**request)
  ├─> Criar kwargs para LTN
  ├─> titulo = LTN(**kwargs)
  │    └─> titulospub/core/ltn/titulo_ltn.py: LTN.__init__()
  │         ├─> self._vm = VariaveisMercado() [ou usa fornecido]
  │         ├─> self._feriados = self._vm.get_feriados()
  │         │    └─> Verifica cache em memória → cache em arquivo → scraping → backup
  │         ├─> self._cdi = self._vm.get_cdi()
  │         ├─> Configurar datas (_configurar_datas)
  │         ├─> Configurar título (_configurar_titulo)
  │         │    └─> Buscar taxa ANBIMA se não fornecida
  │         │         └─> self._vm.get_anbimas()["LTN"]
  │         ├─> Configurar taxa (_configurar_taxa)
  │         │    └─> Se premio+DI fornecido: taxa = di + premio
  │         ├─> Inicializar atributos derivados
  │         ├─> self._calcular()
  │         │    └─> titulospub/core/ltn/calculo_ltn.py: calcular_ltn()
  │         │         ├─> Calcula PU à vista (pu_d0)
  │         │         ├─> Calcula PU a termo (pu_termo)
  │         │         ├─> Calcula DV01
  │         │         ├─> Calcula PU carregado
  │         │         └─> Calcula carregamento
  │         └─> self._financeiro = self._quantidade * self._pu_termo
  ├─> Construir LTNResponse
  │    └─> Serializar todos atributos calculados
  └─> Retornar JSON
       {
         "tipo": "LTN",
         "nome": "LTN 2025",
         "data_vencimento": "2025-01-01",
         "taxa": 12.5,
         "quantidade": 50000,
         "financeiro": 123456.78,
         "pu_d0": 2.4691,
         "pu_termo": 2.4691,
         "dv01": 123.45,
         ...
       }
```

## 3. Criação de Carteira

```
Cliente HTTP
  └─> POST /carteiras/ltn
       {
         "dias_liquidacao": 1,
         "quantidade_padrao": 50000
       }
       
api/routers/carteiras.py: criar_carteira(tipo="ltn", request)
  ├─> CarteiraLTN(data_base, dias_liquidacao, quantidade_padrao)
  │    └─> titulospub/core/carteiras/carteira_ltn.py: CarteiraLTN.__init__()
  │         └─> self._titulos = {} [dicionário vazio]
  ├─> get_vencimentos_ltn()
  │    └─> titulospub/dados/vencimentos.py: get_vencimentos_ltn()
  │         └─> vm = VariaveisMercado()
  │              └─> vm.get_anbimas()["LTN"]["VENCIMENTO"].unique()
  ├─> Para cada vencimento:
  │    ├─> titulo = LTN(data_vencimento_titulo=venc, quantidade=quantidade_padrao)
  │    └─> carteira.adicionar_titulo(venc, titulo)
  │         └─> self._titulos[venc] = titulo
  ├─> Gerar ID único para carteira
  ├─> Armazenar em dicionário global: CARTEIRAS[carteira_id] = carteira
  └─> Retornar CarteiraResponse
       {
         "carteira_id": "abc123",
         "tipo": "LTN",
         "total_titulos": 13,
         "titulos": [...]
       }
```

## 4. Atualização de Taxa em Carteira

```
Cliente HTTP
  └─> PUT /carteiras/{carteira_id}/taxa
       {
         "vencimento": "2025-01-01",
         "taxa": 13.0
       }
       
api/routers/carteiras.py: atualizar_taxa(carteira_id, request)
  ├─> Obter carteira: carteira = CARTEIRAS[carteira_id]
  ├─> carteira.atualizar_taxa(request.vencimento, request.taxa)
  │    └─> titulospub/core/carteiras/carteira_ltn.py: atualizar_taxa()
  │         ├─> titulo = self._titulos[vencimento]
  │         ├─> Criar novo título com nova taxa
  │         │    └─> novo_titulo = LTN(..., taxa=nova_taxa, quantidade=titulo.quantidade)
  │         └─> self._titulos[vencimento] = novo_titulo
  └─> Retornar CarteiraResponse atualizado
```

## 5. Inicialização do Dash

```
run_dash_app.py
  └─> from dash_app.app import app
       └─> app.run(debug=False, port=8050, host="0.0.0.0")
            └─> dash_app/app.py: app = dash.Dash(...)
                 ├─> Define layout (navbar + container)
                 ├─> Define callback de routing
                 │    └─> @app.callback(Output("page-content"), Input("url"))
                 │         └─> render_page(pathname)
                 │              ├─> Se "/ltn": return ltn.layout()
                 │              ├─> Se "/lft": return lft.layout()
                 │              └─> ...
                 └─> Servidor Dash iniciado na porta 8050
```

## 6. Interação no Dash (Exemplo: Página LTN)

```
Usuário acessa http://localhost:8050/ltn
  └─> Callback render_page("/ltn")
       └─> dash_app/pages/ltn.py: layout()
            └─> Retorna HTML com:
                 ├─> Input de dias de liquidação
                 ├─> Tabela de vencimentos (vazia inicialmente)
                 ├─> Botão "Criar Carteira"
                 └─> Seção de equivalência

Usuário clica "Criar Carteira"
  └─> Callback criar_carteira_ltn()
       ├─> dash_app/utils/carteiras.py: criar_carteira("ltn", ...)
       │    └─> dash_app/utils/api.py: post(f"{API_URL}/carteiras/ltn", data)
       │         └─> Requisição HTTP POST para API
       │              └─> [Fluxo 3: Criação de Carteira]
       ├─> Receber resposta com carteira_id e dados
       ├─> Armazenar carteira_id em dcc.Store
       └─> Atualizar tabela com dados da carteira
            └─> Callback renderizar_tabela_ltn()
                 └─> Criar dash_table.DataTable com dados editáveis

Usuário edita taxa na tabela
  └─> Callback atualizar_taxa_ltn()
       ├─> Obter carteira_id do dcc.Store
       ├─> dash_app/utils/carteiras.py: atualizar_taxa(carteira_id, vencimento, nova_taxa)
       │    └─> dash_app/utils/api.py: put(f"{API_URL}/carteiras/{id}/taxa", data)
       │         └─> Requisição HTTP PUT para API
       │              └─> [Fluxo 4: Atualização de Taxa]
       ├─> Receber resposta com dados atualizados
       └─> Atualizar tabela com novos valores
```

## 7. Cálculo de Equivalência

```
Usuário preenche formulário de equivalência
  └─> Título 1: LTN 2025-01-01, Quantidade: 10000
  └─> Título 2: NTNB 2035-05-15
  └─> Critério: DV01
  └─> Clica "Calcular Equivalência"

Callback calcular_equivalencia_ltn()
  ├─> dash_app/utils/api.py: post(f"{API_URL}/equivalencia", data)
  │    └─> Requisição HTTP POST para API
  │         └─> api/routers/equivalencia.py: calcular_equivalencia(request)
  │              ├─> Validação: EquivalenciaRequest(**request)
  │              ├─> titulospub/core/equivalencia.py: equivalencia(...)
  │              │    ├─> Criar título1 = LTN("2025-01-01", quantidade=10000)
  │              │    │    └─> [Fluxo 2: Criação de Título]
  │              │    ├─> Calcular métrica1 = título1.dv01
  │              │    ├─> Criar título2 = NTNB("2035-05-15")
  │              │    │    └─> [Fluxo 2: Criação de Título]
  │              │    ├─> Calcular quantidade equivalente:
  │              │    │    quantidade2 = métrica1 / título2.dv01
  │              │    └─> Retornar quantidade2
  │              └─> Retornar EquivalenciaResponse
  │                   {
  │                     "titulo1": "LTN",
  │                     "venc1": "2025-01-01",
  │                     "qtd1": 10000,
  │                     "titulo2": "NTNB",
  │                     "venc2": "2035-05-15",
  │                     "equivalencia": 5234.56,
  │                     "criterio": "dv"
  │                   }
  └─> Exibir resultado na interface
```

## 8. Atualização Automática de Mercado

```
Cron job ou requisição manual
  └─> POST /atualizar-mercado
  
api/main.py: forcar_atualizacao_mercado()
  ├─> vm = VariaveisMercado()
  ├─> vm.atualizar_tudo(verbose=True)
  │    └─> [Similar ao Fluxo 1, mas força atualização]
  ├─> marcar_atualizado()
  └─> Retornar status de sucesso
```

## Pontos Importantes

1. **Cache em múltiplas camadas:**
   - Memória (atributos `_*` em VariaveisMercado)
   - Arquivo (pickle via cache.py)
   - Verificação antes de fazer scraping

2. **Fallback automático:**
   - Scraping → Backup (Excel) → Erro
   - Sempre tenta scraping primeiro, usa backup se falhar

3. **Estado de carteiras:**
   - Mantido em dicionário global em memória
   - Perdido se servidor reiniciar
   - Não compartilhado entre múltiplos workers

4. **Separação de responsabilidades:**
   - Dash nunca importa titulospub diretamente
   - Toda comunicação via HTTP
   - API é única camada que importa titulospub
