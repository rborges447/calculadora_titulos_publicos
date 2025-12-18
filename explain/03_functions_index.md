# Índice de Funções e Classes

## Classes Principais

### Classes de Títulos

#### `NTNB` (titulospub/core/ntnb/titulo_ntnb.py)
- `__init__(data_vencimento_titulo, data_base=None, dias_liquidacao=1, taxa=None, premio=None, quantidade=10000, ...)` - Inicializa título NTN-B
- `quantidade` (property) - Getter/setter de quantidade de títulos
- `financeiro` (property) - Getter/setter de valor financeiro em R$
- `pu_d0` (property) - Preço unitário à vista
- `pu_termo` (property) - Preço unitário a termo
- `dv01` (property) - DV01 (sensibilidade a 1bp)
- `carrego_brl` (property) - Carregamento em reais
- `carrego_bps` (property) - Carregamento em pontos base
- `duration` (property) - Duration de Macaulay
- `hedge_dap` (property) - Quantidade de contratos DAP para hedge

#### `LTN` (titulospub/core/ltn/titulo_ltn.py)
- `__init__(data_vencimento_titulo, data_base=None, dias_liquidacao=1, taxa=None, premio=None, di=None, quantidade=50000, ...)` - Inicializa título LTN
- `quantidade` (property) - Getter/setter de quantidade
- `financeiro` (property) - Getter/setter de valor financeiro
- `pu_d0` (property) - Preço unitário à vista
- `pu_termo` (property) - Preço unitário a termo
- `dv01` (property) - DV01
- `carrego_brl` (property) - Carregamento em reais
- `hedge_di` (property) - Quantidade de contratos DI para hedge

#### `LFT` (titulospub/core/lft/titulo_lft.py)
- `__init__(data_vencimento_titulo, data_base=None, dias_liquidacao=1, taxa=None, quantidade=10000, ...)` - Inicializa título LFT
- `quantidade` (property) - Getter/setter de quantidade
- `financeiro` (property) - Getter/setter de valor financeiro
- `pu_d0` (property) - Preço unitário à vista
- `pu_termo` (property) - Preço unitário a termo
- `cotacao` (property) - Cotação do título

#### `NTNF` (titulospub/core/ntnf/titulo_ntnf.py)
- `__init__(data_vencimento_titulo, data_base=None, dias_liquidacao=1, taxa=None, premio=None, di=None, quantidade=50000, ...)` - Inicializa título NTN-F
- Propriedades similares a LTN

#### `DI` (titulospub/core/di/di_contrato.py)
- `__init__(codigo, taxa=None, quantidade=1000, ...)` - Inicializa contrato DI
- `quantidade` (property) - Getter/setter de quantidade
- `financeiro` (property) - Getter/setter de valor financeiro
- `pu` (property) - Preço unitário
- `dv01` (property) - DV01

### Classes de Carteiras

#### `CarteiraNTNB` (titulospub/core/carteiras/carteira_ntnb.py)
- `__init__(data_base=None, dias_liquidacao=1, quantidade_padrao=None)` - Inicializa carteira NTNB
- `adicionar_titulo(vencimento, titulo)` - Adiciona título à carteira
- `remover_titulo(vencimento)` - Remove título da carteira
- `atualizar_taxa(vencimento, nova_taxa)` - Atualiza taxa de um título
- `atualizar_dias_liquidacao(novos_dias)` - Atualiza dias de liquidação globalmente
- `get_dados()` - Retorna dados formatados da carteira
- `get_total_quantidade()` - Retorna quantidade total
- `get_total_financeiro()` - Retorna financeiro total
- `get_total_dv01()` - Retorna DV01 total

#### `CarteiraLTN`, `CarteiraLFT`, `CarteiraNTNF`
- Métodos similares a CarteiraNTNB
- CarteiraLTN e CarteiraNTNF têm `atualizar_premio_di(vencimento, premio, di)`

### Classe de Orquestração

#### `VariaveisMercado` (titulospub/dados/orquestrador.py)
- `__init__()` - Inicializa orquestrador (cache vazio)
- `get_feriados(force_update=False)` - Obtém lista de feriados
- `get_ipca_dict(data=None, feriados=None, force_update=False)` - Obtém dicionário IPCA
- `get_cdi(force_update=False)` - Obtém taxa CDI
- `get_vna_lft(force_update=False)` - Obtém VNA LFT
- `get_anbimas(force_update=False)` - Obtém dados ANBIMA
- `get_bmf(force_update=False)` - Obtém dados BMF
- `atualizar_tudo(verbose=False)` - Atualiza todas variáveis

## Funções de Cálculo

### NTNB

#### `calculo_ntnb()` (titulospub/core/ntnb/calculo_ntnb.py)
- `calculo_duration(datas_cupons_ajustadas, data_liquidacao, pv_fluxos)` - Calcula duration
- `data_vencimento_duration(data_liquidacao, duration)` - Calcula data de vencimento da duration
- `dias_uteis_duration(data_liquidacao, data_venc_duration, feriados=None)` - Calcula dias úteis até duration
- `calculo_dv01_ntnb(duration, pu, taxa)` - Calcula DV01
- `cauculo_pu_carregado(data, data_liquidacao, pu, cdi=None, feriados=None)` - Calcula PU carregado
- `calculo_pu_ajustado(data, data_liquidacao, taxa, pu, ipca_dict=None, feriados=None)` - Calcula PU ajustado
- `calculo_carrego_ntnb(pu_carregado, pu_ajustado, dv01)` - Calcula carregamento
- `calculo_taxa_pu_ntnb(vna_ajustado, cotacao)` - Calcula taxa a partir de PU
- `calculo_dv01_ntnb(data_vencimento, data_liquidacao, taxa, vna_ajustado, feriados=None)` - Calcula DV01 completo
- `calculo_ntnb(data, data_liquidacao, data_vencimento, taxa, cdi=None, ipca_dict=None, feriados=None)` - Função principal

#### `vna_ntnb.py`
- `calculo_vna_ntnb(data, ipca_dict=None, feriados=None)` - Calcula VNA base
- `calculo_vna_ajustado_ntnb(data, data_liquidacao, ipca_dict=None, feriados=None, leilao=False)` - Calcula VNA ajustado
- `fator_ipca(data, data_liquidacao, ipca_dict=None, feriados=None)` - Calcula fator IPCA

#### `cash_flow_ntnb.py`
- `datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia=2, feriados=None)` - Calcula datas de cupons
- `fv_cupons(datas_cupons, taxa_cupom=6)` - Calcula valor futuro dos cupons
- `calcular_pv_cupons(datas_cupons_ajustadas, data_liquidacao, feriados, taxa, taxa_cupom=6)` - Calcula valor presente
- `cash_flow_ntnb(data_vencimento, data_liquidacao, taxa, feriados=None, taxa_cupom=6, frequencia=2)` - Função principal

### LTN

#### `calculo_ltn.py`
- `taxa_pu_ltn(data, data_liquidacao, data_vencimento, taxa, feriados=None)` - Calcula PU a partir de taxa
- `pu_taxa_ltn(data, data_liquidacao, data_vencimento, pu, feriados=None)` - Calcula taxa a partir de PU
- `calculo_dv01_ltn(data, data_liquidacao, data_vencimento, taxa, feriados=None)` - Calcula DV01
- `calculo_carrego_ltn(pu, pu_carregado, dv01)` - Calcula carregamento
- `calcular_ltn(data, data_liquidacao, data_vencimento, taxa, cdi=None, feriados=None)` - Função principal

### LFT

#### `calculo_lft.py`
- `pu_cotcao_lft(taxa, data_liquidacao, data_vencimento, feriados=None)` - Calcula PU a partir de cotação
- `taxa_pu_lft(data, data_liquidacao, data_vencimento, taxa, ...)` - Calcula taxa a partir de PU
- `calcular_lft(data, data_liquidacao, data_vencimento, taxa, ...)` - Função principal

#### `ajuste_vna_lft.py`
- `calculo_vna_ajustado_lft(data, data_liquidacao, cdi=None, vna_lft=None, feriados=None)` - Calcula VNA ajustado

### NTNF

#### `calculo_ntnf.py`
- `taxa_pu_ntnf(data_liquidacao, data_vencimento, taxa, feriados=None)` - Calcula PU a partir de taxa
- `calculo_dv01_ntnf(data_liquidacao, data_vencimento, taxa, feriados=None)` - Calcula DV01
- `calculo_carrego_ntnf(pu, pu_carregado, dv01)` - Calcula carregamento
- `calcular_ntnf(data, data_liquidacao, data_vencimento, taxa, cdi=None, feriados=None)` - Função principal

#### `cash_flow_ntnf.py`
- `f_v_ntnf(datas_cupons_ajustadas)` - Calcula valor futuro dos cupons
- `cotacao_ntnf(fv, dias_entre_datas, taxa)` - Calcula cotação

### DI

#### `calculo_di.py`
- `taxa_pu_di(taxa, codigo=None, data_liquidacao=None, data_vencimento=None, feriados=None)` - Calcula PU a partir de taxa
- `calculo_dv01_di(taxa, codigo=None, data_liquidacao=None, data_vencimento=None, feriados=None)` - Calcula DV01

### DAP

#### `calculo_dap.py`
- `dia_15_do_mes(data)` - Retorna dia 15 do mês (vencimento DAP)
- `calculo_prt(data=None, ipca_dict=None)` - Calcula PRT (Preço de Referência de Títulos)
- `calculo_pu_dap(taxa, codigo=None, data_liquidacao=None, data_vencimento=None, feriados=None)` - Calcula PU DAP
- `calculo_financeiro_dap(taxa, codigo=None, data_liquidacao=None, data_vencimento=None, feriados=None)` - Calcula financeiro DAP
- `dv01_dap(taxa, codigo=None, data_liquidacao=None, data_vencimento=None, feriados=None)` - Calcula DV01 DAP

### Equivalência

#### `equivalencia.py`
- `equivalencia(titulo1, venc1, titulo2, venc2, qtd1, criterio='dv', tx1=None, tx2=None)` - Calcula equivalência entre títulos

### Auxiliares

#### `auxilio.py`
- `calculo_pu_carregado(data, data_liquidacao, pu, cdi=None, feriados=None)` - Calcula PU carregado genérico
- `codigo_vencimento_bmf(codigo)` - Converte código BMF para data de vencimento
- `vencimento_codigo_bmf(data_vencimento, prefixo)` - Converte data para código BMF

## Funções de Dados

### Cache

#### `cache.py`
- `save_cache(data, filename)` - Salva dados em arquivo pickle
- `load_cache(filename)` - Carrega dados de arquivo pickle
- `clear_cache(filename)` - Remove arquivo de cache

### Backup

#### `backup.py`
- `backup_cdi()` - Lê CDI de arquivo Excel
- `backup_feriados()` - Lê feriados de arquivo Excel
- `backup_ipca_fechado()` - Lê IPCA fechado de arquivo Excel
- `backup_ipca_proj()` - Lê IPCA projetado de arquivo Excel
- `backup_anbimas()` - Lê dados ANBIMA de arquivo Excel
- `backup_bmf()` - Lê dados BMF de arquivo Excel

### Processamento

#### `anbimas.py`
- `anbimas(anbima_df)` - Processa DataFrame ANBIMA e retorna dicionário por tipo

#### `bmf.py`
- `ajustes_bmf(data)` - Processa dados BMF e retorna dicionário com DI e DAP
- `ajustes_bmf_net(bmf_dict, data=None)` - Processa dados BMF Net

#### `ipca.py`
- `inicio_fim_mes_ipca(data, feriados=None)` - Calcula início e fim do mês IPCA
- `dicionario_ipca(data, ipca_fechado_df, ipca_proj_float, feriados=None)` - Cria dicionário de IPCA

#### `vencimentos.py`
- `get_vencimentos_ltn()` - Retorna lista de vencimentos LTN
- `get_vencimentos_lft()` - Retorna lista de vencimentos LFT
- `get_vencimentos_ntnb()` - Retorna lista de vencimentos NTNB
- `get_vencimentos_ntnf()` - Retorna lista de vencimentos NTNF
- `get_codigos_di_disponiveis()` - Retorna lista de códigos DI
- `get_todos_vencimentos()` - Retorna todos vencimentos organizados

## Funções de Scraping

#### `anbima_scraping.py`
- `scrap_anbimas(data)` - Scraping de taxas indicativas ANBIMA
- `scrap_cdi()` - Scraping de taxa CDI
- `scrap_feriados()` - Scraping de lista de feriados
- `scrap_proj_ipca()` - Scraping de IPCA projetado
- `scrap_vna_lft(data)` - Scraping de VNA LFT

#### `sidra_scraping.py`
- `puxar_valores_ipca_fechado()` - Obtém valores de IPCA fechado via API SIDRA

#### `bmf_net_scraping.py`
- `scrap_bmf_net()` - Scraping de dados BMF Net

#### `uptodata_scraping.py`
- `definir_caminho_adj_bmf(data)` - Define caminho de arquivo de ajustes BMF
- `scrap_ajustes_bmf(data)` - Scraping de ajustes BMF

## Funções Utilitárias

### Datas

#### `datas.py`
- `adicionar_dias_uteis(data, n_dias, feriados=None)` - Adiciona N dias úteis
- `e_dia_util(data, feriados=None)` - Verifica se é dia útil
- `dias_trabalho_total(data_inicio, data_fim, feriados=None)` - Calcula total de dias úteis
- `listar_dias_entre_datas(data_liquidacao, datas, feriados=None)` - Lista dias úteis entre datas
- `ajustar_para_proximo_dia_util(datas, feriados=None)` - Ajusta para próximo dia útil
- `listar_datas(data_inicio, data_fim)` - Lista todas datas entre duas datas
- `data_vencimento_ajustada(data, feriados=None)` - Ajusta data de vencimento
- `datas_pagamento_cupons(data_vencimento, data_liquidacao, frequencia=2, feriados=None)` - Calcula datas de cupons

### Paths

#### `paths.py`
- `path_backup_csv(nome_arquivo)` - Retorna caminho para CSV de backup
- `path_backup_pickle(nome_arquivo)` - Retorna caminho para pickle de backup
- `path_logs(nome_arquivo)` - Retorna caminho para arquivo de log

### Carregamento

#### `carregamento_var_globais.py`
- `_carregar_feriados_se_necessario(feriados)` - Carrega feriados se None
- `_carrecar_ipca_dict_se_necessario(ipca_dict)` - Carrega IPCA dict se None
- `_carrecar_cdi_se_necessario(cdi)` - Carrega CDI se None
- `_carregar_vna_lft_se_necessario(vna_lft)` - Carrega VNA LFT se None

## Funções da API

### Utils

#### `api/utils.py`
- `serialize_datetime(dt)` - Serializa datetime para string ISO
- `precisa_atualizar_mercado()` - Verifica se precisa atualizar mercado
- `marcar_atualizado()` - Marca que mercado foi atualizado
- `get_ultima_atualizacao()` - Obtém data da última atualização

## Funções do Dash

### API

#### `dash_app/utils/api.py`
- `get(url)` - Requisição GET
- `post(url, data)` - Requisição POST
- `put(url, data)` - Requisição PUT

### Carteiras

#### `dash_app/utils/carteiras.py`
- `criar_carteira(tipo, data_base=None, dias_liquidacao=1, quantidade_padrao=None)` - Cria carteira via API
- `atualizar_taxa(carteira_id, vencimento, taxa)` - Atualiza taxa via API
- `atualizar_premio_di(carteira_id, vencimento, premio, di)` - Atualiza prêmio e DI via API
- `atualizar_dias_liquidacao(carteira_id, dias)` - Atualiza dias via API

### Formatação

#### `dash_app/utils/formatacao.py`
- `formatar_taxa_brasileira(valor)` - Formata taxa como porcentagem brasileira
- `formatar_pu_brasileiro(valor)` - Formata PU brasileiro
- `parse_numero_brasileiro(texto)` - Parse de número brasileiro (vírgula decimal)
- `formatar_bps(valor)` - Formata pontos base
- `formatar_dv01(valor)` - Formata DV01
- `formatar_inteiro(valor)` - Formata inteiro
- `formatar_numero_brasileiro(valor)` - Formata número genérico brasileiro

### Vencimentos

#### `dash_app/utils/vencimentos.py`
- `formatar_data_para_exibicao(data)` - Formata data para exibição
