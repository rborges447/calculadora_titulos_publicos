"""
Página NTNB - tabela editável usando carteiras.
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from dash_app.utils.carteiras import criar_carteira, atualizar_taxa, atualizar_dias_liquidacao
from dash_app.utils.vencimentos import formatar_data_para_exibicao
from dash_app.utils.formatacao import (
    formatar_taxa_brasileira, 
    formatar_pu_brasileiro, 
    parse_numero_brasileiro,
    formatar_bps,
    formatar_dv01,
    formatar_inteiro,
    formatar_numero_brasileiro,
)
from dash_app.utils.api import post, get
from dash_app.config import API_URL


def layout():
    return dbc.Container(
        [
            dcc.Store(id="ntnb-carteira-id", data=None),
            dcc.Store(id="ntnb-dados-originais", data=[]),
            html.H2("NTNB - Nota do Tesouro Nacional - Série B", className="mb-3"),
            
            # ==================== TOPO GLOBAL - DIAS LIQUIDAÇÃO ====================
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Dias para liquidação", className="fw-bold"),
                                        dbc.Input(
                                            id="ntnb-dias",
                                            type="number",
                                            value=1,
                                            min=0,
                                            className="mt-2",
                                        ),
                                    ],
                                    md=3,
                                ),
                            ],
                        ),
                    ]
                ),
                className="mb-4",
            ),
            
            # ==================== CONTAINER PRINCIPAL EM 2 COLUNAS ====================
            dbc.Row(
                [
                    # ==================== COLUNA ESQUERDA ====================
                    dbc.Col(
                        [
                            # Tabela de Vencimentos
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("Tabela de Vencimentos", className="mb-3"),
                                        html.Div(
                                            id="ntnb-tabela-container",
                                            style={"maxHeight": "500px", "overflowY": "auto"},
                                        ),
                                    ]
                                ),
                                className="mb-4",
                                style={"maxHeight": "600px", "display": "flex", "flexDirection": "column"},
                            ),
                            
                            # Equivalência entre Títulos
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("Equivalência entre Títulos", className="mb-3"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Título A"),
                                                        dcc.Dropdown(
                                                            id="ntnb-eq-titulo-a",
                                                            placeholder="Selecione o título A",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Título B"),
                                                        dcc.Dropdown(
                                                            id="ntnb-eq-titulo-b",
                                                            placeholder="Selecione o título B",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Quantidade A"),
                                                        dbc.Input(
                                                            id="ntnb-eq-quantidade-a",
                                                            type="number",
                                                            value=10000,
                                                            min=0,
                                                            step=1,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Taxa A (%)"),
                                                        dbc.Input(
                                                            id="ntnb-eq-taxa-a",
                                                            type="text",
                                                            placeholder="Vazio = usa ANBIMA",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Taxa B (%)"),
                                                        dbc.Input(
                                                            id="ntnb-eq-taxa-b",
                                                            type="text",
                                                            placeholder="Vazio = usa ANBIMA",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Critério"),
                                                        dcc.Dropdown(
                                                            id="ntnb-eq-criterio",
                                                            options=[
                                                                {"label": "DV01", "value": "DV01"},
                                                                {"label": "FRA", "value": "FRA"},
                                                            ],
                                                            value="DV01",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Calcular",
                                            id="ntnb-eq-calcular",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="ntnb-eq-resultado"),
                                    ]
                                ),
                            ),
                        ],
                        md=6,
                    ),
                    
                    # ==================== COLUNA DIREITA ====================
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("Calculadora Detalhada", className="mb-3"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Vencimento"),
                                                        dcc.Dropdown(
                                                            id="ntnb-calc-vencimento",
                                                            placeholder="Selecione o vencimento",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    md=12,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Taxa (%)"),
                                                        dbc.Input(
                                                            id="ntnb-calc-taxa",
                                                            type="text",
                                                            placeholder="Vazio = usa ANBIMA",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Modo"),
                                                        dcc.Dropdown(
                                                            id="ntnb-calc-modo",
                                                            options=[
                                                                {"label": "Quantidade", "value": "Quantidade"},
                                                                {"label": "Financeiro", "value": "Financeiro"},
                                                            ],
                                                            value="Quantidade",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            [
                                                                dbc.Label(id="ntnb-calc-valor-label", children="Quantidade"),
                                                                dbc.Input(
                                                                    id="ntnb-calc-valor",
                                                                    type="number",
                                                                    min=0,
                                                                    step=1,
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("DI Futuro"),
                                                        dcc.Dropdown(
                                                            id="ntnb-calc-di",
                                                            placeholder="Opcional",
                                                            clearable=True,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Calcular",
                                            id="ntnb-calc-calcular",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="ntnb-calc-resultado"),
                                        html.Hr(className="my-3"),
                                        html.P(
                                            [
                                                "Para calcular o hedge DI, acesse a página dedicada: ",
                                                dcc.Link(
                                                    "Ir para Hedge DI →",
                                                    href="/ntnb/hedge-di",
                                                    style={
                                                        "text-decoration": "none",
                                                        "font-weight": "500",
                                                    },
                                                ),
                                            ],
                                            className="text-muted small mb-0",
                                        ),
                                    ]
                                ),
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="g-4",
            ),
        ],
        fluid=True,
        className="py-2",
    )


@callback(
    [
        Output("ntnb-carteira-id", "data"),
        Output("ntnb-dados-originais", "data"),
        Output("ntnb-tabela-container", "children"),
    ],
    [
        Input("ntnb-dias", "value"),
    ],
    State("ntnb-carteira-id", "data"),
    prevent_initial_call=False,
)
def carregar_carteira(dias, carteira_id_existente):
    """Carrega ou atualiza a carteira"""
    from dash import ctx
    
    try:
        # Permitir 0 como valor válido (dias or 1 trataria 0 como False)
        dias = dias if dias is not None else 1
        
        # Se já existe uma carteira, atualizar os dias de liquidação
        if carteira_id_existente:
            print(f"[INFO] Atualizando dias de liquidação para {dias} na carteira existente...")
            ok, resultado = atualizar_dias_liquidacao("ntnb", carteira_id_existente, dias)
            if ok:
                carteira_id = carteira_id_existente
            else:
                # Se falhou (ex: carteira não existe mais), criar nova
                print(f"[INFO] Falha ao atualizar dias, criando nova carteira...")
                ok, resultado = criar_carteira("ntnb", dias_liquidacao=dias)
                if not ok:
                    return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
                carteira_id = resultado.get("carteira_id")
        else:
            # Criar nova carteira
            print(f"[INFO] Criando nova carteira com {dias} dias de liquidação...")
            ok, resultado = criar_carteira("ntnb", dias_liquidacao=dias)
            if not ok:
                return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
            carteira_id = resultado.get("carteira_id")
        
        # Obter dias de liquidação para exibir no nome da coluna PU
        dias_liquidacao_atual = resultado.get("dias_liquidacao", dias if dias is not None else 1)
        nome_pu = f"PU D{dias_liquidacao_atual}"
        
        dados = [
            {
                "vencimento": formatar_data_para_exibicao(t["vencimento"]),
                "vencimento_raw": t["vencimento"],
                "taxa_anbima": formatar_taxa_brasileira(t.get("taxa_anbima")) if t.get("taxa_anbima") is not None else "",
                "taxa": formatar_taxa_brasileira(t.get("taxa")) if t.get("taxa") is not None else "",
                "pu_termo": formatar_pu_brasileiro(t.get("pu_termo")) if t.get("pu_termo") is not None else "",
                "carrego_bps": formatar_bps(t.get("carrego_bps")) if t.get("carrego_bps") is not None else "",
                "premio_dap": formatar_bps(t.get("premio_anbima_dap")) if t.get("premio_anbima_dap") is not None else "",
                "hedge_dap": formatar_inteiro(t.get("hedge_dap")) if t.get("hedge_dap") is not None else "",
                "dv01": formatar_dv01(t.get("dv01")) if t.get("dv01") is not None else "",
            }
            for t in resultado["titulos"]
        ]
        
        tabela = dash_table.DataTable(
            id="ntnb-tabela",
            columns=[
                {"name": "Vencimento", "id": "vencimento", "editable": False},
                {"name": "Anbima", "id": "taxa_anbima", "editable": False, "type": "text"},
                {"name": "Taxa %", "id": "taxa", "editable": True, "type": "text"},
                {"name": nome_pu, "id": "pu_termo", "editable": False, "type": "text"},
                {"name": "Carry BPS", "id": "carrego_bps", "editable": False, "type": "text"},
                {"name": "Premio Casada", "id": "premio_dap", "editable": False, "type": "text"},
                {"name": "Hedge Casada", "id": "hedge_dap", "editable": False, "type": "text"},
                {"name": "DV01 BRL", "id": "dv01", "editable": False, "type": "text"},
            ],
            data=dados,
            editable=True,
            style_cell={
                "textAlign": "left", 
                "padding": "8px",
                "fontSize": "12px",
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_header={
                "backgroundColor": "#0d6efd", 
                "color": "white", 
                "fontWeight": "bold",
                "fontSize": "12px",
                "textAlign": "center",
            },
            style_data={
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_table={
                "overflowX": "auto",
                "maxHeight": "500px",
                "overflowY": "auto",
                "width": "100%",
            },
            fixed_rows={"headers": True},
            page_size=15,
            virtualization=True,
        )
        
        # Atualizar dados originais para comparação
        return carteira_id, dados, tabela
    except Exception as e:
        print(f"[ERRO] Erro ao carregar carteira: {e}")
        import traceback
        traceback.print_exc()
        return None, [], html.P(f"Erro ao carregar carteira: {e}", className="text-danger")


@callback(
    [
        Output("ntnb-tabela", "data", allow_duplicate=True),
        Output("ntnb-carteira-id", "data", allow_duplicate=True),
        Output("ntnb-dados-originais", "data", allow_duplicate=True),
    ],
    [
        Input("ntnb-tabela", "data_timestamp"),
    ],
    [
        State("ntnb-tabela", "data"),
        State("ntnb-tabela", "active_cell"),
        State("ntnb-carteira-id", "data"),
        State("ntnb-dados-originais", "data"),
        State("ntnb-dias", "value"),
    ],
    prevent_initial_call=True,
)
def atualizar_taxa_callback(timestamp, data_atual, active_cell, carteira_id, dados_originais, dias):
    """Atualiza taxa quando editada"""
    from dash import ctx
    
    # Se não há dados, retornar
    if not data_atual:
        return data_atual or [], carteira_id, dados_originais or []
    
    # Determinar qual linha foi editada usando o vencimento_raw, não o índice
    row_idx = None
    vencimento_raw = None
    nova_taxa = None
    col_id = None
    
    # Priorizar active_cell se disponível (mais confiável)
    if active_cell:
        row_idx = active_cell.get("row")
        col_id = active_cell.get("column_id")
        if col_id != "taxa":
            return data_atual, carteira_id, dados_originais or []
        
        # Usar o vencimento_raw da linha editada para identificar o título correto
        if row_idx is not None and row_idx < len(data_atual):
            linha_editada = data_atual[row_idx]
            vencimento_raw = linha_editada.get("vencimento_raw")
            nova_taxa = linha_editada.get("taxa")
            
            # VALIDAÇÃO: Comparar com dados originais para garantir que estamos na linha certa
            # Se a taxa na linha row_idx não mudou em relação aos dados originais, pode ser que
            # o active_cell esteja apontando para a linha errada
            if dados_originais and row_idx < len(dados_originais):
                linha_original = dados_originais[row_idx]
                taxa_original = str(linha_original.get("taxa", "")).strip()
                taxa_atual = str(nova_taxa or "").strip()
                
                if taxa_original == taxa_atual:
                    # A taxa não mudou nesta linha - procurar em todas as linhas qual realmente mudou
                    for i, (orig, atual) in enumerate(zip(dados_originais, data_atual)):
                        taxa_orig = str(orig.get("taxa", "")).strip()
                        taxa_at = str(atual.get("taxa", "")).strip()
                        if taxa_orig != taxa_at:
                            # Usar esta linha em vez da do active_cell
                            vencimento_raw = atual.get("vencimento_raw")
                            nova_taxa = atual.get("taxa")
                            row_idx = i
                            break
        else:
            return data_atual, carteira_id, dados_originais or []
    else:
        # Se não há active_cell, comparar com dados originais para encontrar mudança
        if dados_originais and len(dados_originais) == len(data_atual):
            mudancas = []
            for i, (original, atual) in enumerate(zip(dados_originais, data_atual)):
                taxa_original = str(original.get("taxa", "")).strip()
                taxa_atual = str(atual.get("taxa", "")).strip()
                if taxa_original != taxa_atual:
                    venc_raw = atual.get("vencimento_raw")
                    mudancas.append((i, taxa_original, taxa_atual, venc_raw))
            
            if len(mudancas) == 1:
                # Apenas uma mudança - usar essa
                row_idx = mudancas[0][0]
                vencimento_raw = mudancas[0][3]
                nova_taxa = mudancas[0][2]
            elif len(mudancas) > 1:
                # Múltiplas mudanças - usar a última (mais recente)
                row_idx = mudancas[-1][0]
                vencimento_raw = mudancas[-1][3]
                nova_taxa = mudancas[-1][2]
            else:
                return data_atual, carteira_id, dados_originais or []
        else:
            return data_atual, carteira_id, dados_originais or []
    
    # Validar que temos os dados necessários
    if not vencimento_raw:
        return data_atual, carteira_id, dados_originais or []
    
    if nova_taxa is None:
        # Se não pegamos a taxa ainda, buscar da linha
        if row_idx is not None and row_idx < len(data_atual):
            nova_taxa = data_atual[row_idx].get("taxa")
        else:
            return data_atual, carteira_id, dados_originais or []
    
    # Encontrar o índice correto na lista atual usando vencimento_raw
    # (caso a tabela tenha sido reordenada)
    row_idx_correto = None
    for i, linha in enumerate(data_atual):
        if linha.get("vencimento_raw") == vencimento_raw:
            row_idx_correto = i
            break
    
    if row_idx_correto is None:
        return data_atual, carteira_id, dados_originais or []
    
    # Usar o índice correto
    row_idx = row_idx_correto
    linha = data_atual[row_idx]
    
    # Verificar se a taxa mudou
    if not nova_taxa or nova_taxa == "":
        # Se taxa foi limpa, limpar campos calculados também
        dados_atualizados = [dict(d) for d in data_atual]  # Deep copy
        dados_atualizados[row_idx]["pu_termo"] = ""
        dados_atualizados[row_idx]["carrego_bps"] = ""
        dados_atualizados[row_idx]["premio_dap"] = ""
        dados_atualizados[row_idx]["hedge_dap"] = ""
        dados_atualizados[row_idx]["dv01"] = ""
        dados_originais_atualizados = [dict(d) for d in dados_atualizados]  # Atualizar originais
        return dados_atualizados, carteira_id, dados_originais_atualizados
    
    # Converter do formato brasileiro para float
    taxa_float = parse_numero_brasileiro(nova_taxa)
    if taxa_float is None:
        return data_atual, carteira_id, dados_originais or []
    
    # Tentar atualizar na carteira existente
    if carteira_id:
        ok, resultado = atualizar_taxa("ntnb", carteira_id, vencimento_raw, taxa_float)
        if ok:
            titulo = next((t for t in resultado.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                # Criar nova lista (deep copy) para garantir que o Dash detecte a mudança
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") is not None else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)  # Formatar no padrão brasileiro
                dados_atualizados[row_idx]["carrego_bps"] = formatar_bps(titulo.get("carrego_bps")) if titulo.get("carrego_bps") is not None else ""
                dados_atualizados[row_idx]["premio_dap"] = formatar_bps(titulo.get("premio_anbima_dap")) if titulo.get("premio_anbima_dap") is not None else ""
                dados_atualizados[row_idx]["hedge_dap"] = formatar_inteiro(titulo.get("hedge_dap")) if titulo.get("hedge_dap") is not None else ""
                dados_atualizados[row_idx]["dv01"] = formatar_dv01(titulo.get("dv01")) if titulo.get("dv01") is not None else ""
                # Atualizar dados originais também
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, carteira_id, dados_originais_atualizados
    
    # Se falhou ou carteira não existe, recriar
    try:
        ok_criar, resultado_criar = criar_carteira("ntnb", dias_liquidacao=dias if dias is not None else 1)
        if not ok_criar:
            return data_atual, None, dados_originais or []
        
        novo_id = resultado_criar.get("carteira_id")
        ok_atualizar, resultado_atualizar = atualizar_taxa("ntnb", novo_id, vencimento_raw, taxa_float)
        
        if ok_atualizar:
            titulo = next((t for t in resultado_atualizar.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                # Criar nova lista (deep copy)
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") is not None else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_atualizados[row_idx]["carrego_bps"] = formatar_bps(titulo.get("carrego_bps")) if titulo.get("carrego_bps") is not None else ""
                dados_atualizados[row_idx]["premio_dap"] = formatar_bps(titulo.get("premio_anbima_dap")) if titulo.get("premio_anbima_dap") is not None else ""
                dados_atualizados[row_idx]["hedge_dap"] = formatar_inteiro(titulo.get("hedge_dap")) if titulo.get("hedge_dap") is not None else ""
                dados_atualizados[row_idx]["dv01"] = formatar_dv01(titulo.get("dv01")) if titulo.get("dv01") is not None else ""
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, novo_id, dados_originais_atualizados
    except Exception as e:
        # Log de erro apenas se necessário (sem print de debug)
        pass
    
    return data_atual, carteira_id, dados_originais or []


# ==================== CALLBACKS PARA POPULAR DROPDOWNS ====================

@callback(
    [
        Output("ntnb-eq-titulo-a", "options"),
        Output("ntnb-eq-titulo-b", "options"),
        Output("ntnb-calc-vencimento", "options"),
    ],
    [
        Input("ntnb-dados-originais", "data"),
    ],
)
def popular_dropdowns(dados_originais):
    """Popula os dropdowns com os vencimentos disponíveis"""
    if not dados_originais:
        return [], [], []
    
    options = [
        {
            "label": d.get("vencimento", ""),
            "value": d.get("vencimento_raw", ""),
        }
        for d in dados_originais
    ]
    
    return options, options, options


@callback(
    Output("ntnb-calc-di", "options"),
    [
        Input("ntnb-dados-originais", "data"),
    ],
    prevent_initial_call=False,
)
def popular_dropdown_di(dados_originais):
    """Popula o dropdown de DI Futuro com os códigos DI disponíveis"""
    # Carregar códigos DI disponíveis da API
    ok, resultado = get("/vencimentos/di", timeout=30)
    
    if not ok:
        return []
    
    # resultado é uma lista de strings com os códigos DI
    if isinstance(resultado, list):
        return [{"label": codigo, "value": codigo} for codigo in resultado]
    
    return []


# ==================== CALLBACK PARA ATUALIZAR LABEL DO CAMPO VALOR ====================

@callback(
    Output("ntnb-calc-valor-label", "children"),
    Input("ntnb-calc-modo", "value"),
)
def atualizar_label_valor(modo):
    """Atualiza o label do campo valor baseado no modo selecionado"""
    return "Quantidade" if modo == "Quantidade" else "Financeiro (R$)"


# ==================== CALLBACK DE EQUIVALÊNCIA ====================

@callback(
    Output("ntnb-eq-resultado", "children"),
    [
        Input("ntnb-eq-calcular", "n_clicks"),
        Input("ntnb-dias", "value"),
    ],
    [
        State("ntnb-eq-titulo-a", "value"),
        State("ntnb-eq-titulo-b", "value"),
        State("ntnb-eq-quantidade-a", "value"),
        State("ntnb-eq-taxa-a", "value"),
        State("ntnb-eq-taxa-b", "value"),
        State("ntnb-eq-criterio", "value"),
        State("ntnb-dados-originais", "data"),
    ],
    prevent_initial_call=True,
)
def calcular_equivalencia(n_clicks, dias_liquidacao, titulo_a, titulo_b, qtd_a, taxa_a, taxa_b, criterio, dados_originais):
    """Calcula equivalência entre títulos"""
    from dash import ctx
    
    # Verificar se foi disparado pelo botão ou pela mudança de dias
    if not ctx.triggered:
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Se foi disparado apenas pela mudança de dias mas não há dados ainda, não fazer nada
    if trigger_id == "ntnb-dias" and (not titulo_a or not titulo_b):
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    # Validar campos obrigatórios
    if not titulo_a or not titulo_b or not qtd_a:
        return html.Div("Preencha todos os campos obrigatórios.", className="text-danger")
    
    # Obter vencimentos formatados para exibição
    venc_a_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == titulo_a), titulo_a)
    venc_b_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == titulo_b), titulo_b)
    
    # Mapear critério
    criterio_api = "dv" if criterio == "DV01" else "fin"
    
    # Preparar payload
    payload = {
        "titulo1": "NTNB",
        "venc1": titulo_a,
        "titulo2": "NTNB",
        "venc2": titulo_b,
        "qtd1": float(qtd_a),
        "criterio": criterio_api,
    }
    
    # Processar taxas
    taxa_a_float = None
    taxa_b_float = None
    
    if taxa_a:
        try:
            taxa_a_float = parse_numero_brasileiro(taxa_a) if taxa_a else None
            if taxa_a_float is not None:
                payload["tx1"] = taxa_a_float
        except:
            pass
    
    if taxa_b:
        try:
            taxa_b_float = parse_numero_brasileiro(taxa_b) if taxa_b else None
            if taxa_b_float is not None:
                payload["tx2"] = taxa_b_float
        except:
            pass
    
    # Chamar API de equivalência
    ok, resultado = post("/equivalencia", payload, timeout=30)
    
    if not ok:
        return html.Div(
            [
                html.H5("Erro ao calcular equivalência", className="text-danger"),
                html.P(str(resultado), className="text-danger"),
            ],
            className="mt-3 p-3 bg-light rounded",
        )
    
    # Exibir resultado
    equivalencia_calculada = resultado.get("equivalencia", 0)
    
    return html.Div(
        [
            html.H5("Resultado da Equivalência", className="mt-3 mb-3"),
            html.Div(
                [
                    html.P([html.Strong("Dias de liquidação: "), str(dias_liquidacao if dias_liquidacao is not None else 1)], className="mb-2"),
                    html.P([html.Strong("Título A: "), venc_a_formatado], className="mb-2"),
                    html.P([html.Strong("Título B: "), venc_b_formatado], className="mb-2"),
                    html.P([html.Strong("Quantidade A: "), formatar_numero_brasileiro(qtd_a, 0)], className="mb-2"),
                    html.P([html.Strong("Taxa A: "), formatar_taxa_brasileira(taxa_a_float) if taxa_a_float is not None else "ANBIMA"], className="mb-2"),
                    html.P([html.Strong("Taxa B: "), formatar_taxa_brasileira(taxa_b_float) if taxa_b_float is not None else "ANBIMA"], className="mb-2"),
                    html.P([html.Strong("Critério: "), criterio], className="mb-3"),
                    html.Hr(className="my-3"),
                    html.Div(
                        [
                            html.H5("Quantidade Equivalente (Título B)", className="text-primary mb-2"),
                            html.P(
                                [
                                    html.Span(formatar_numero_brasileiro(equivalencia_calculada, 2), style={"fontSize": "24px", "fontWeight": "bold", "color": "#0d6efd"}),
                                ],
                                className="mb-0",
                            ),
                        ],
                        className="text-center p-3 bg-white rounded border",
                    ),
                ],
            ),
        ],
        className="mt-3 p-3 bg-light rounded",
    )


# ==================== CALLBACK DE CALCULADORA ====================

@callback(
    Output("ntnb-calc-resultado", "children"),
    [
        Input("ntnb-calc-calcular", "n_clicks"),
        Input("ntnb-dias", "value"),
    ],
    [
        State("ntnb-calc-vencimento", "value"),
        State("ntnb-calc-taxa", "value"),
        State("ntnb-calc-modo", "value"),
        State("ntnb-calc-valor", "value"),
        State("ntnb-calc-di", "value"),
        State("ntnb-dados-originais", "data"),
    ],
    prevent_initial_call=True,
)
def calcular_detalhado(n_clicks, dias_liquidacao, vencimento, taxa, modo, valor, di_futuro, dados_originais):
    """Calcula título detalhado"""
    from dash import ctx
    
    # Verificar se foi disparado pelo botão ou pela mudança de dias
    if not ctx.triggered:
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Se foi disparado apenas pela mudança de dias mas não há dados ainda, não fazer nada
    if trigger_id == "ntnb-dias" and (not vencimento or not valor):
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    # Validar campos obrigatórios
    if not vencimento or not valor:
        return html.Div("Preencha todos os campos obrigatórios.", className="text-danger")
    
    # Obter vencimento formatado para exibição
    venc_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == vencimento), vencimento)
    
    # Preparar payload para API
    dias_liquidacao = dias_liquidacao if dias_liquidacao is not None else 1
    payload = {
        "data_vencimento": vencimento,
        "dias_liquidacao": dias_liquidacao,
    }
    
    # Adicionar taxa se fornecida
    if taxa:
        try:
            taxa_float = parse_numero_brasileiro(taxa)
            if taxa_float is not None:
                payload["taxa"] = taxa_float
        except:
            pass
    
    # Adicionar quantidade ou financeiro baseado no modo
    try:
        valor_float = float(valor)
        if modo == "Quantidade":
            payload["quantidade"] = valor_float
        else:
            payload["financeiro"] = valor_float
    except:
        return html.Div("Valor inválido.", className="text-danger")
    
    # Armazenar valor_float para uso posterior (hedge DI)
    valor_float_calculado = valor_float
    
    # Chamar API
    ok, resultado = post("/titulos/ntnb", payload, timeout=30)
    
    if not ok:
        return html.Div(
            [
                html.H5("Erro ao calcular", className="text-danger"),
                html.P(str(resultado), className="text-danger"),
            ],
            className="mt-3 p-3 bg-light rounded",
        )
    
    # Organizar resultados em seções
    resultado_items = []
    
    # Informações básicas
    resultado_items.append(html.H5("Informações Básicas", className="mt-3 mb-2"))
    resultado_items.append(html.P([html.Strong("Nome: "), resultado.get("nome", "-")]))
    resultado_items.append(html.P([html.Strong("Data de vencimento: "), resultado.get("data_vencimento", "-")]))
    resultado_items.append(html.P([html.Strong("Data base: "), resultado.get("data_base", "-")]))
    resultado_items.append(html.P([html.Strong("Data de liquidação: "), resultado.get("data_liquidacao", "-")]))
    resultado_items.append(html.P([html.Strong("Dias de liquidação: "), str(resultado.get("dias_liquidacao", "-"))]))
    
    # Taxas
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Taxas", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Taxa ANBIMA: "), formatar_taxa_brasileira(resultado.get("taxa_anbima")) if resultado.get("taxa_anbima") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Taxa: "), formatar_taxa_brasileira(resultado.get("taxa")) if resultado.get("taxa") is not None else "-"]))
    
    # Quantidade e Financeiro
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Posição", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Quantidade: "), formatar_numero_brasileiro(resultado.get("quantidade"), 0) if resultado.get("quantidade") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Financeiro: "), formatar_numero_brasileiro(resultado.get("financeiro"), 2) if resultado.get("financeiro") is not None else "-"]))
    
    # Preços Unitários
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Preços Unitários", className="mb-2"))
    resultado_items.append(html.P([html.Strong("PU D0: "), formatar_pu_brasileiro(resultado.get("pu_d0")) if resultado.get("pu_d0") is not None else "-"]))
    resultado_items.append(html.P([html.Strong(f"PU D{dias_liquidacao}: "), formatar_pu_brasileiro(resultado.get("pu_termo")) if resultado.get("pu_termo") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("PU Carregado: "), formatar_pu_brasileiro(resultado.get("pu_carregado")) if resultado.get("pu_carregado") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("PU Ajustado: "), formatar_pu_brasileiro(resultado.get("pu_ajustado")) if resultado.get("pu_ajustado") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Cotação: "), formatar_pu_brasileiro(resultado.get("cotacao")) if resultado.get("cotacao") is not None else "-"]))
    
    # Sensibilidade e Carregamento
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Sensibilidade e Carregamento", className="mb-2"))
    resultado_items.append(html.P([html.Strong("DV01: "), formatar_dv01(resultado.get("dv01")) if resultado.get("dv01") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Carregamento BRL: "), formatar_numero_brasileiro(resultado.get("carrego_brl"), 2) if resultado.get("carrego_brl") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Carregamento BPS: "), formatar_bps(resultado.get("carrego_bps")) if resultado.get("carrego_bps") is not None else "-"]))
    
    # Duration
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Duration", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Duration: "), formatar_numero_brasileiro(resultado.get("duration"), 4) if resultado.get("duration") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Data vencimento duration: "), resultado.get("data_vencimento_duration", "-")]))
    resultado_items.append(html.P([html.Strong("Dias até duration: "), str(resultado.get("dias_duration", "-")) if resultado.get("dias_duration") is not None else "-"]))
    
    # DAP e Prêmio
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("DAP e Prêmio", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Ajuste DAP: "), formatar_taxa_brasileira(resultado.get("ajuste_dap")) if resultado.get("ajuste_dap") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Prêmio: "), formatar_bps(resultado.get("premio")) if resultado.get("premio") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Prêmio ANBIMA DAP: "), formatar_bps(resultado.get("premio_anbima_dap")) if resultado.get("premio_anbima_dap") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Hedge DAP: "), formatar_inteiro(resultado.get("hedge_dap")) if resultado.get("hedge_dap") is not None else "-"]))
    
    # VNA
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("VNA", className="mb-2"))
    resultado_items.append(html.P([html.Strong("VNA Ajustado: "), formatar_pu_brasileiro(resultado.get("vna")) if resultado.get("vna") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("VNA Tesouro: "), formatar_pu_brasileiro(resultado.get("vna_tesouro")) if resultado.get("vna_tesouro") is not None else "-"]))
    
    # Equivalência com DI (se DI Futuro foi selecionado)
    if di_futuro:
        resultado_items.append(html.Hr(className="my-3"))
        resultado_items.append(html.H5("Equivalência com DI", className="mb-2"))
        
        # Calcular hedge DI usando o endpoint específico
        payload_hedge = {
            "data_vencimento": vencimento,
            "codigo_di": di_futuro,
            "dias_liquidacao": dias_liquidacao,
        }
        
        # Adicionar taxa se fornecida
        if taxa:
            try:
                taxa_float = parse_numero_brasileiro(taxa)
                if taxa_float is not None:
                    payload_hedge["taxa"] = taxa_float
            except:
                pass
        
        # Adicionar quantidade ou financeiro baseado no modo
        if modo == "Quantidade":
            payload_hedge["quantidade"] = valor_float_calculado
        else:
            payload_hedge["financeiro"] = valor_float_calculado
        
        # Chamar API de hedge DI
        ok_hedge, resultado_hedge = post("/titulos/ntnb/hedge-di", payload_hedge, timeout=30)
        
        if ok_hedge:
            hedge_di = resultado_hedge.get("hedge_di", 0)
            dv01_ntnb = resultado_hedge.get("dv01_ntnb", 0)
            ajuste_di = resultado_hedge.get("ajuste_di")
            
            resultado_items.append(html.P([html.Strong("Código DI: "), di_futuro], className="mb-2"))
            resultado_items.append(html.P([html.Strong("Ajuste DI: "), formatar_taxa_brasileira(ajuste_di) if ajuste_di is not None else "-"], className="mb-2"))
            resultado_items.append(html.P([html.Strong("DV01 NTNB: "), formatar_dv01(dv01_ntnb) if dv01_ntnb is not None else "-"], className="mb-3"))
            resultado_items.append(html.Div(
                [
                    html.H5("Hedge DI (Quantidade de Contratos)", className="text-primary mb-2"),
                    html.P(
                        [
                            html.Span(formatar_inteiro(hedge_di), style={"fontSize": "24px", "fontWeight": "bold", "color": "#0d6efd"}),
                        ],
                        className="mb-0",
                    ),
                ],
                className="text-center p-3 bg-white rounded border",
            ))
        else:
            resultado_items.append(html.P([html.Strong("Erro ao calcular hedge DI: "), str(resultado_hedge)], className="text-danger mb-2"))
    
    return html.Div(
        resultado_items,
        className="mt-3 p-3 bg-light rounded",
        style={"maxHeight": "600px", "overflowY": "auto"},
    )
