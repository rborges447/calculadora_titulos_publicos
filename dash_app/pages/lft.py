"""
Página LFT - tabela editável usando carteiras.
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from dash_app.utils.carteiras import criar_carteira, atualizar_taxa, atualizar_dias_liquidacao
from dash_app.utils.vencimentos import formatar_data_para_exibicao
from dash_app.utils.formatacao import (
    formatar_taxa_brasileira, 
    formatar_pu_brasileiro, 
    parse_numero_brasileiro,
    formatar_numero_brasileiro,
)
from dash_app.utils.api import post, get
from dash_app.config import API_URL


def layout():
    return dbc.Container(
        [
            dcc.Store(id="lft-carteira-id", data=None),
            dcc.Store(id="lft-dados-originais", data=[]),
            html.H2("LFT - Letra Financeira do Tesouro", className="mb-3"),
            
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
                                            id="lft-dias",
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
                                            id="lft-tabela-container",
                                            style={"maxHeight": "500px", "overflowY": "auto", "overflowX": "auto", "width": "100%"},
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
                                                            id="lft-eq-titulo-a",
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
                                                            id="lft-eq-titulo-b",
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
                                                            id="lft-eq-quantidade-a",
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
                                                        dbc.Label("Critério"),
                                                        dcc.Dropdown(
                                                            id="lft-eq-criterio",
                                                            options=[
                                                                {"label": "FRA", "value": "FRA"},
                                                            ],
                                                            value="FRA",
                                                            clearable=False,
                                                            disabled=True,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Alert(
                                            "LFT só suporta equivalência por financeiro (FRA).",
                                            color="info",
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Taxa A (%)"),
                                                        dbc.Input(
                                                            id="lft-eq-taxa-a",
                                                            type="text",
                                                            placeholder="Vazio = usa ANBIMA",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Taxa B (%)"),
                                                        dbc.Input(
                                                            id="lft-eq-taxa-b",
                                                            type="text",
                                                            placeholder="Vazio = usa ANBIMA",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Calcular",
                                            id="lft-eq-calcular",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="lft-eq-resultado"),
                                    ]
                                ),
                                className="mb-4",
                            ),
                        ],
                        md=6,
                    ),
                    
                    # ==================== COLUNA DIREITA - CALCULADORA DETALHADA ====================
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
                                                            id="lft-calc-vencimento",
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
                                                            id="lft-calc-taxa",
                                                            type="text",
                                                            placeholder="Vazio = usa ANBIMA",
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
                                                        dbc.Label("Modo"),
                                                        dcc.Dropdown(
                                                            id="lft-calc-modo",
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
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            [
                                                                dbc.Label(id="lft-calc-valor-label", children="Quantidade"),
                                                                dbc.Input(
                                                                    id="lft-calc-valor",
                                                                    type="number",
                                                                    min=0,
                                                                    step=1,
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Calcular",
                                            id="lft-calc-calcular",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="lft-calc-resultado"),
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
        Output("lft-carteira-id", "data"),
        Output("lft-dados-originais", "data"),
        Output("lft-tabela-container", "children"),
    ],
    [
        Input("lft-dias", "value"),
    ],
    State("lft-carteira-id", "data"),
    prevent_initial_call=False,
)
def carregar_carteira(dias, carteira_id_existente):
    """Carrega ou atualiza a carteira"""
    try:
        dias = dias if dias is not None else 1
        
        if carteira_id_existente:
            ok, resultado = atualizar_dias_liquidacao("lft", carteira_id_existente, dias)
            if ok:
                carteira_id = carteira_id_existente
            else:
                ok, resultado = criar_carteira("lft", dias_liquidacao=dias)
                if not ok:
                    return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
                carteira_id = resultado.get("carteira_id")
        else:
            ok, resultado = criar_carteira("lft", dias_liquidacao=dias)
            if not ok:
                return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
            carteira_id = resultado.get("carteira_id")
        
        dias_liquidacao_atual = resultado.get("dias_liquidacao", dias if dias is not None else 1)
        nome_pu = f"PU D{dias_liquidacao_atual}"
        
        dados = [
            {
                "vencimento": formatar_data_para_exibicao(t["vencimento"]),
                "vencimento_raw": t["vencimento"],
                "taxa_anbima": formatar_taxa_brasileira(t.get("taxa_anbima")) if t.get("taxa_anbima") is not None else "",
                "taxa": formatar_taxa_brasileira(t.get("taxa")) if t.get("taxa") is not None else "",
                "pu_termo": formatar_pu_brasileiro(t.get("pu_termo")) if t.get("pu_termo") is not None else "",
            }
            for t in resultado["titulos"]
        ]
        
        tabela = dash_table.DataTable(
            id="lft-tabela",
            columns=[
                {"name": "Vencimento", "id": "vencimento", "editable": False},
                {"name": "Anbima", "id": "taxa_anbima", "editable": False, "type": "text"},
                {"name": "Taxa", "id": "taxa", "editable": True, "type": "text"},
                {"name": nome_pu, "id": "pu_termo", "editable": False, "type": "text"},
            ],
            data=dados,
            editable=True,
            style_cell={
                "textAlign": "left", 
                "padding": "5px",
                "fontSize": "11px",
                "whiteSpace": "normal",
                "height": "auto",
                "minWidth": "80px",
                "maxWidth": "120px",
            },
            style_header={
                "backgroundColor": "#0d6efd", 
                "color": "white", 
                "fontWeight": "bold",
                "fontSize": "11px",
                "textAlign": "center",
            },
            style_data={
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_table={
                "overflowX": "auto",
                "overflowY": "auto",
                "maxHeight": "500px",
                "width": "100%",
                "minWidth": "100%",
            },
            fixed_rows={"headers": True},
            page_size=15,
            virtualization=True,
        )
        
        return carteira_id, dados, tabela
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, [], html.P(f"Erro ao carregar carteira: {e}", className="text-danger")


@callback(
    [
        Output("lft-tabela", "data", allow_duplicate=True),
        Output("lft-carteira-id", "data", allow_duplicate=True),
        Output("lft-dados-originais", "data", allow_duplicate=True),
    ],
    [
        Input("lft-tabela", "data_timestamp"),
    ],
    [
        State("lft-tabela", "data"),
        State("lft-tabela", "active_cell"),
        State("lft-carteira-id", "data"),
        State("lft-dados-originais", "data"),
        State("lft-dias", "value"),
    ],
    prevent_initial_call=True,
)
def atualizar_taxa_callback(timestamp, data_atual, active_cell, carteira_id, dados_originais, dias):
    """Atualiza taxa quando editada"""
    if not data_atual:
        return data_atual or [], carteira_id, dados_originais or []
    
    row_idx = None
    vencimento_raw = None
    nova_taxa = None
    
    if active_cell:
        row_idx = active_cell.get("row")
        col_id = active_cell.get("column_id")
        if col_id != "taxa":
            return data_atual, carteira_id, dados_originais or []
        
        if row_idx is not None and row_idx < len(data_atual):
            linha_editada = data_atual[row_idx]
            vencimento_raw = linha_editada.get("vencimento_raw")
            nova_taxa = linha_editada.get("taxa")
            
            if dados_originais and row_idx < len(dados_originais):
                linha_original = dados_originais[row_idx]
                taxa_original = str(linha_original.get("taxa", "")).strip()
                taxa_atual = str(nova_taxa or "").strip()
                
                if taxa_original == taxa_atual:
                    for i, (orig, atual) in enumerate(zip(dados_originais, data_atual)):
                        taxa_orig = str(orig.get("taxa", "")).strip()
                        taxa_at = str(atual.get("taxa", "")).strip()
                        if taxa_orig != taxa_at:
                            vencimento_raw = atual.get("vencimento_raw")
                            nova_taxa = atual.get("taxa")
                            row_idx = i
                            break
        else:
            return data_atual, carteira_id, dados_originais or []
    else:
        if dados_originais and len(dados_originais) == len(data_atual):
            mudancas = []
            for i, (original, atual) in enumerate(zip(dados_originais, data_atual)):
                taxa_original = str(original.get("taxa", "")).strip()
                taxa_atual = str(atual.get("taxa", "")).strip()
                if taxa_original != taxa_atual:
                    venc_raw = atual.get("vencimento_raw")
                    mudancas.append((i, taxa_original, taxa_atual, venc_raw))
            
            if len(mudancas) == 1:
                row_idx = mudancas[0][0]
                vencimento_raw = mudancas[0][3]
                nova_taxa = mudancas[0][2]
            elif len(mudancas) > 1:
                row_idx = mudancas[-1][0]
                vencimento_raw = mudancas[-1][3]
                nova_taxa = mudancas[-1][2]
            else:
                return data_atual, carteira_id, dados_originais or []
        else:
            return data_atual, carteira_id, dados_originais or []
    
    if not vencimento_raw:
        return data_atual, carteira_id, dados_originais or []
    
    if nova_taxa is None:
        if row_idx is not None and row_idx < len(data_atual):
            nova_taxa = data_atual[row_idx].get("taxa")
        else:
            return data_atual, carteira_id, dados_originais or []
    
    row_idx_correto = None
    for i, linha in enumerate(data_atual):
        if linha.get("vencimento_raw") == vencimento_raw:
            row_idx_correto = i
            break
    
    if row_idx_correto is None:
        return data_atual, carteira_id, dados_originais or []
    
    row_idx = row_idx_correto
    
    if not nova_taxa or nova_taxa == "":
        dados_atualizados = [dict(d) for d in data_atual]
        dados_atualizados[row_idx]["pu_termo"] = ""
        dados_originais_atualizados = [dict(d) for d in dados_atualizados]
        return dados_atualizados, carteira_id, dados_originais_atualizados
    
    taxa_float = parse_numero_brasileiro(nova_taxa)
    if taxa_float is None:
        return data_atual, carteira_id, dados_originais or []
    
    if carteira_id:
        ok, resultado = atualizar_taxa("lft", carteira_id, vencimento_raw, taxa_float)
        if ok:
            titulo = next((t for t in resultado.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") is not None else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, carteira_id, dados_originais_atualizados
    
    try:
        ok_criar, resultado_criar = criar_carteira("lft", dias_liquidacao=dias if dias is not None else 1)
        if not ok_criar:
            return data_atual, None, dados_originais or []
        
        novo_id = resultado_criar.get("carteira_id")
        ok_atualizar, resultado_atualizar = atualizar_taxa("lft", novo_id, vencimento_raw, taxa_float)
        
        if ok_atualizar:
            titulo = next((t for t in resultado_atualizar.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") is not None else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, novo_id, dados_originais_atualizados
    except Exception as e:
        pass
    
    return data_atual, carteira_id, dados_originais or []


# ==================== CALLBACKS PARA POPULAR DROPDOWNS ====================

@callback(
    [
        Output("lft-eq-titulo-a", "options"),
        Output("lft-eq-titulo-b", "options"),
        Output("lft-calc-vencimento", "options"),
    ],
    [
        Input("lft-dados-originais", "data"),
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
    Output("lft-calc-valor-label", "children"),
    Input("lft-calc-modo", "value"),
)
def atualizar_label_valor(modo):
    return "Quantidade" if modo == "Quantidade" else "Financeiro (R$)"


# ==================== CALLBACK DE EQUIVALÊNCIA ====================

@callback(
    Output("lft-eq-resultado", "children"),
    [Input("lft-eq-calcular", "n_clicks"), Input("lft-dias", "value")],
    [
        State("lft-eq-titulo-a", "value"),
        State("lft-eq-titulo-b", "value"),
        State("lft-eq-quantidade-a", "value"),
        State("lft-eq-taxa-a", "value"),
        State("lft-eq-taxa-b", "value"),
        State("lft-eq-criterio", "value"),
        State("lft-dados-originais", "data"),
    ],
    prevent_initial_call=True,
)
def calcular_equivalencia(n_clicks, dias_liquidacao, titulo_a, titulo_b, qtd_a, taxa_a, taxa_b, criterio, dados_originais):
    from dash import ctx
    if not ctx.triggered:
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "lft-dias" and (not titulo_a or not titulo_b):
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    if not titulo_a or not titulo_b or not qtd_a:
        return html.Div("Preencha todos os campos obrigatórios.", className="text-danger")
    
    venc_a_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == titulo_a), titulo_a)
    venc_b_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == titulo_b), titulo_b)
    criterio_api = "fin"  # LFT só suporta financeiro
    
    # Por padrão, assume LFT para ambos (já que estamos na página LFT)
    # Mas a API aceita qualquer tipo de título
    tipo_a = "LFT"
    tipo_b = "LFT"
    
    payload = {
        "titulo1": tipo_a,
        "venc1": titulo_a,
        "titulo2": tipo_b,
        "venc2": titulo_b,
        "qtd1": float(qtd_a),
        "criterio": criterio_api
    }
    
    taxa_a_float = None
    taxa_b_float = None
    
    if taxa_a:
        try:
            taxa_a_float = parse_numero_brasileiro(taxa_a)
            if taxa_a_float is not None:
                payload["tx1"] = taxa_a_float
        except:
            pass
    if taxa_b:
        try:
            taxa_b_float = parse_numero_brasileiro(taxa_b)
            if taxa_b_float is not None:
                payload["tx2"] = taxa_b_float
        except:
            pass
    
    ok, resultado = post("/equivalencia", payload, timeout=30)
    
    if not ok:
        return html.Div(
            [
                html.H5("Erro ao calcular equivalência", className="text-danger"),
                html.P(str(resultado), className="text-danger"),
            ],
            className="mt-3 p-3 bg-light rounded",
        )
    
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
                    html.P([html.Strong("Critério: "), "FRA (Financeiro)"], className="mb-3"),
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
    Output("lft-calc-resultado", "children"),
    [
        Input("lft-calc-calcular", "n_clicks"),
        Input("lft-dias", "value"),
    ],
    [
        State("lft-calc-vencimento", "value"),
        State("lft-calc-taxa", "value"),
        State("lft-calc-modo", "value"),
        State("lft-calc-valor", "value"),
        State("lft-dados-originais", "data"),
    ],
    prevent_initial_call=True,
)
def calcular_detalhado(n_clicks, dias_liquidacao, vencimento, taxa, modo, valor, dados_originais):
    """Calcula título detalhado"""
    from dash import ctx
    
    if not ctx.triggered:
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "lft-dias" and (not vencimento or not valor):
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    if not vencimento or not valor:
        return html.Div("Preencha todos os campos obrigatórios.", className="text-danger")
    
    venc_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == vencimento), vencimento)
    
    dias_liquidacao = dias_liquidacao if dias_liquidacao is not None else 1
    payload = {
        "data_vencimento": vencimento,
        "dias_liquidacao": dias_liquidacao,
    }
    
    if taxa:
        try:
            taxa_float = parse_numero_brasileiro(taxa)
            if taxa_float is not None:
                payload["taxa"] = taxa_float
        except:
            pass
    
    try:
        valor_float = float(valor)
        if modo == "Quantidade":
            payload["quantidade"] = valor_float
        else:
            payload["financeiro"] = valor_float
    except:
        return html.Div("Valor inválido.", className="text-danger")
    
    ok, resultado = post("/titulos/lft", payload, timeout=30)
    
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
    pu_termo_valor = resultado.get("pu_termo")
    resultado_items.append(html.P([html.Strong(f"PU D{dias_liquidacao}: "), formatar_pu_brasileiro(pu_termo_valor) if pu_termo_valor is not None else "-"]))
    resultado_items.append(html.P([html.Strong("PU Carregado: "), formatar_pu_brasileiro(resultado.get("pu_carregado")) if resultado.get("pu_carregado") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Cotação: "), formatar_pu_brasileiro(resultado.get("cotacao")) if resultado.get("cotacao") is not None else "-"]))
    
    return html.Div(
        resultado_items,
        className="mt-3 p-3 bg-light rounded",
        style={"maxHeight": "600px", "overflowY": "auto"},
    )
