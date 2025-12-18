"""
Página LTN - tabela editável usando carteiras.
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from dash_app.utils.carteiras import criar_carteira, atualizar_taxa, atualizar_premio_di, atualizar_dias_liquidacao
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
            dcc.Store(id="ltn-carteira-id", data=None),
            dcc.Store(id="ltn-dados-originais", data=[]),
            html.H2("LTN - Letra do Tesouro Nacional", className="mb-3"),
            
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
                                            id="ltn-dias",
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
                                            id="ltn-tabela-container",
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
                                                            id="ltn-eq-titulo-a",
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
                                                            id="ltn-eq-titulo-b",
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
                                                            id="ltn-eq-quantidade-a",
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
                                                            id="ltn-eq-criterio",
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
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Taxa A (%)"),
                                                        dbc.Input(
                                                            id="ltn-eq-taxa-a",
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
                                                            id="ltn-eq-taxa-b",
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
                                            id="ltn-eq-calcular",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="ltn-eq-resultado"),
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
                                                            id="ltn-calc-vencimento",
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
                                                        dbc.Label("Tipo de entrada"),
                                                        dcc.Dropdown(
                                                            id="ltn-calc-tipo",
                                                            options=[
                                                                {"label": "Taxa (%)", "value": "taxa"},
                                                                {"label": "Prêmio + DI", "value": "premio_di"},
                                                            ],
                                                            value="taxa",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            [
                                                                dbc.Label(id="ltn-calc-taxa-label", children="Taxa (%)"),
                                                                dbc.Input(
                                                                    id="ltn-calc-taxa",
                                                                    type="text",
                                                                    placeholder="Vazio = usa ANBIMA",
                                                                ),
                                                            ],
                                                            id="ltn-calc-box-taxa",
                                                        ),
                                                    ],
                                                    md=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("Prêmio (%)"),
                                                                dbc.Input(
                                                                    id="ltn-calc-premio",
                                                                    type="text",
                                                                    placeholder="Ex: 0.5",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Label("DI (%)"),
                                                                dbc.Input(
                                                                    id="ltn-calc-di-valor",
                                                                    type="text",
                                                                    placeholder="Ex: 13.0",
                                                                ),
                                                            ],
                                                            md=6,
                                                        ),
                                                    ],
                                                    className="mb-3",
                                                ),
                                            ],
                                            id="ltn-calc-box-premio-di",
                                            style={"display": "none"},
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Modo"),
                                                        dcc.Dropdown(
                                                            id="ltn-calc-modo",
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
                                                                dbc.Label(id="ltn-calc-valor-label", children="Quantidade"),
                                                                dbc.Input(
                                                                    id="ltn-calc-valor",
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
                                            id="ltn-calc-calcular",
                                            color="primary",
                                            className="mb-3",
                                        ),
                                        html.Div(id="ltn-calc-resultado"),
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
        Output("ltn-carteira-id", "data"),
        Output("ltn-dados-originais", "data"),
        Output("ltn-tabela-container", "children"),
    ],
    [
        Input("ltn-dias", "value"),
    ],
    State("ltn-carteira-id", "data"),
    prevent_initial_call=False,
)
def carregar_carteira(dias, carteira_id_existente):
    """Carrega ou atualiza a carteira"""
    try:
        dias = dias if dias is not None else 1
        
        if carteira_id_existente:
            ok, resultado = atualizar_dias_liquidacao("ltn", carteira_id_existente, dias)
            if ok:
                carteira_id = carteira_id_existente
            else:
                ok, resultado = criar_carteira("ltn", dias_liquidacao=dias)
                if not ok:
                    return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
                carteira_id = resultado.get("carteira_id")
        else:
            ok, resultado = criar_carteira("ltn", dias_liquidacao=dias)
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
                "carrego_bps": formatar_bps(t.get("carrego_bps")) if t.get("carrego_bps") is not None else "",
                "dv01": formatar_dv01(t.get("dv01")) if t.get("dv01") is not None else "",
                "ajuste_di": formatar_taxa_brasileira(t.get("ajuste_di")) if t.get("ajuste_di") is not None else "",
                "premio_anbima": formatar_bps(t.get("premio_anbima")) if t.get("premio_anbima") is not None else "",
            }
            for t in resultado["titulos"]
        ]
        
        tabela = dash_table.DataTable(
            id="ltn-tabela",
            columns=[
                {"name": "Vencimento", "id": "vencimento", "editable": False},
                {"name": "Anbima", "id": "taxa_anbima", "editable": False, "type": "text"},
                {"name": "Taxa %", "id": "taxa", "editable": True, "type": "text"},
                {"name": nome_pu, "id": "pu_termo", "editable": False, "type": "text"},
                {"name": "Carry BPS", "id": "carrego_bps", "editable": False, "type": "text"},
                {"name": "DV01 BRL", "id": "dv01", "editable": False, "type": "text"},
                {"name": "Ajuste DI", "id": "ajuste_di", "editable": False, "type": "text"},
                {"name": "Premio Anbima", "id": "premio_anbima", "editable": False, "type": "text"},
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
        Output("ltn-tabela", "data", allow_duplicate=True),
        Output("ltn-carteira-id", "data", allow_duplicate=True),
        Output("ltn-dados-originais", "data", allow_duplicate=True),
    ],
    [
        Input("ltn-tabela", "data_timestamp"),
    ],
    [
        State("ltn-tabela", "data"),
        State("ltn-tabela", "active_cell"),
        State("ltn-carteira-id", "data"),
        State("ltn-dados-originais", "data"),
        State("ltn-dias", "value"),
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
        dados_atualizados[row_idx]["carrego_bps"] = ""
        dados_atualizados[row_idx]["dv01"] = ""
        dados_atualizados[row_idx]["ajuste_di"] = ""
        dados_atualizados[row_idx]["premio_anbima"] = ""
        dados_originais_atualizados = [dict(d) for d in dados_atualizados]
        return dados_atualizados, carteira_id, dados_originais_atualizados
    
    taxa_float = parse_numero_brasileiro(nova_taxa)
    if taxa_float is None:
        return data_atual, carteira_id, dados_originais or []
    
    if carteira_id:
        ok, resultado = atualizar_taxa("ltn", carteira_id, vencimento_raw, taxa_float)
        if ok:
            titulo = next((t for t in resultado.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") is not None else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_atualizados[row_idx]["carrego_bps"] = formatar_bps(titulo.get("carrego_bps")) if titulo.get("carrego_bps") is not None else ""
                dados_atualizados[row_idx]["dv01"] = formatar_dv01(titulo.get("dv01")) if titulo.get("dv01") is not None else ""
                dados_atualizados[row_idx]["ajuste_di"] = formatar_taxa_brasileira(titulo.get("ajuste_di")) if titulo.get("ajuste_di") is not None else ""
                dados_atualizados[row_idx]["premio_anbima"] = formatar_bps(titulo.get("premio_anbima")) if titulo.get("premio_anbima") is not None else ""
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, carteira_id, dados_originais_atualizados
    
    try:
        ok_criar, resultado_criar = criar_carteira("ltn", dias_liquidacao=dias if dias is not None else 1)
        if not ok_criar:
            return data_atual, None, dados_originais or []
        
        novo_id = resultado_criar.get("carteira_id")
        ok_atualizar, resultado_atualizar = atualizar_taxa("ltn", novo_id, vencimento_raw, taxa_float)
        
        if ok_atualizar:
            titulo = next((t for t in resultado_atualizar.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") is not None else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_atualizados[row_idx]["carrego_bps"] = formatar_bps(titulo.get("carrego_bps")) if titulo.get("carrego_bps") is not None else ""
                dados_atualizados[row_idx]["dv01"] = formatar_dv01(titulo.get("dv01")) if titulo.get("dv01") is not None else ""
                dados_atualizados[row_idx]["ajuste_di"] = formatar_taxa_brasileira(titulo.get("ajuste_di")) if titulo.get("ajuste_di") is not None else ""
                dados_atualizados[row_idx]["premio_anbima"] = formatar_bps(titulo.get("premio_anbima")) if titulo.get("premio_anbima") is not None else ""
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, novo_id, dados_originais_atualizados
    except Exception as e:
        pass
    
    return data_atual, carteira_id, dados_originais or []


# ==================== CALLBACKS PARA POPULAR DROPDOWNS ====================

@callback(
    [
        Output("ltn-eq-titulo-a", "options"),
        Output("ltn-eq-titulo-b", "options"),
        Output("ltn-calc-vencimento", "options"),
    ],
    [
        Input("ltn-dados-originais", "data"),
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
    Output("ltn-calc-valor-label", "children"),
    Input("ltn-calc-modo", "value"),
)
def atualizar_label_valor(modo):
    return "Quantidade" if modo == "Quantidade" else "Financeiro (R$)"


@callback(
    [
        Output("ltn-calc-box-taxa", "style"),
        Output("ltn-calc-box-premio-di", "style"),
        Output("ltn-calc-taxa-label", "children"),
    ],
    Input("ltn-calc-tipo", "value"),
)
def alternar_campos_calculadora(tipo):
    """Alterna entre campos de taxa e premio+DI"""
    if tipo == "premio_di":
        return {"display": "none"}, {"display": "block"}, "Taxa (%)"
    else:
        return {"display": "block"}, {"display": "none"}, "Taxa (%)"


# ==================== CALLBACK DE EQUIVALÊNCIA ====================

@callback(
    Output("ltn-eq-resultado", "children"),
    [Input("ltn-eq-calcular", "n_clicks"), Input("ltn-dias", "value")],
    [
        State("ltn-eq-titulo-a", "value"),
        State("ltn-eq-titulo-b", "value"),
        State("ltn-eq-quantidade-a", "value"),
        State("ltn-eq-taxa-a", "value"),
        State("ltn-eq-taxa-b", "value"),
        State("ltn-eq-criterio", "value"),
        State("ltn-dados-originais", "data"),
    ],
    prevent_initial_call=True,
)
def calcular_equivalencia(n_clicks, dias_liquidacao, titulo_a, titulo_b, qtd_a, taxa_a, taxa_b, criterio, dados_originais):
    from dash import ctx
    if not ctx.triggered:
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "ltn-dias" and (not titulo_a or not titulo_b):
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    if not titulo_a or not titulo_b or not qtd_a:
        return html.Div("Preencha todos os campos obrigatórios.", className="text-danger")
    
    venc_a_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == titulo_a), titulo_a)
    venc_b_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == titulo_b), titulo_b)
    criterio_api = "dv" if criterio == "DV01" else "fin"
    
    payload = {"titulo1": "LTN", "venc1": titulo_a, "titulo2": "LTN", "venc2": titulo_b, "qtd1": float(qtd_a), "criterio": criterio_api}
    
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
    Output("ltn-calc-resultado", "children"),
    [
        Input("ltn-calc-calcular", "n_clicks"),
        Input("ltn-dias", "value"),
    ],
    [
        State("ltn-calc-vencimento", "value"),
        State("ltn-calc-tipo", "value"),
        State("ltn-calc-taxa", "value"),
        State("ltn-calc-premio", "value"),
        State("ltn-calc-di-valor", "value"),
        State("ltn-calc-modo", "value"),
        State("ltn-calc-valor", "value"),
        State("ltn-dados-originais", "data"),
    ],
    prevent_initial_call=True,
)
def calcular_detalhado(n_clicks, dias_liquidacao, vencimento, tipo, taxa, premio, di_valor, modo, valor, dados_originais):
    """Calcula título detalhado"""
    from dash import ctx
    
    if not ctx.triggered:
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "ltn-dias" and (not vencimento or not valor):
        return html.Div("Preencha os campos e clique em Calcular.", className="text-muted")
    
    if not vencimento or not valor:
        return html.Div("Preencha todos os campos obrigatórios.", className="text-danger")
    
    venc_formatado = next((d.get("vencimento") for d in dados_originais if d.get("vencimento_raw") == vencimento), vencimento)
    
    dias_liquidacao = dias_liquidacao if dias_liquidacao is not None else 1
    payload = {
        "data_vencimento": vencimento,
        "dias_liquidacao": dias_liquidacao,
    }
    
    if tipo == "taxa":
        if taxa:
            try:
                taxa_float = parse_numero_brasileiro(taxa)
                if taxa_float is not None:
                    payload["taxa"] = taxa_float
            except:
                pass
    elif tipo == "premio_di":
        if premio:
            try:
                premio_float = parse_numero_brasileiro(premio)
                if premio_float is not None:
                    payload["premio"] = premio_float
            except:
                pass
        if di_valor:
            try:
                di_float = parse_numero_brasileiro(di_valor)
                if di_float is not None:
                    payload["di"] = di_float
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
    
    valor_float_calculado = valor_float
    
    ok, resultado = post("/titulos/ltn", payload, timeout=30)
    
    if not ok:
        return html.Div(
            [
                html.H5("Erro ao calcular", className="text-danger"),
                html.P(str(resultado), className="text-danger"),
            ],
            className="mt-3 p-3 bg-light rounded",
        )
    
    resultado_items = []
    
    resultado_items.append(html.H5("Informações Básicas", className="mt-3 mb-2"))
    resultado_items.append(html.P([html.Strong("Nome: "), resultado.get("nome", "-")]))
    resultado_items.append(html.P([html.Strong("Data de vencimento: "), resultado.get("data_vencimento", "-")]))
    resultado_items.append(html.P([html.Strong("Data base: "), resultado.get("data_base", "-")]))
    resultado_items.append(html.P([html.Strong("Data de liquidação: "), resultado.get("data_liquidacao", "-")]))
    resultado_items.append(html.P([html.Strong("Dias de liquidação: "), str(resultado.get("dias_liquidacao", "-"))]))
    
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Taxas", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Taxa ANBIMA: "), formatar_taxa_brasileira(resultado.get("taxa_anbima")) if resultado.get("taxa_anbima") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Taxa: "), formatar_taxa_brasileira(resultado.get("taxa")) if resultado.get("taxa") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Prêmio: "), formatar_bps(resultado.get("premio")) if resultado.get("premio") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("DI: "), formatar_taxa_brasileira(resultado.get("di")) if resultado.get("di") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Ajuste DI: "), formatar_taxa_brasileira(resultado.get("ajuste_di")) if resultado.get("ajuste_di") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Prêmio ANBIMA: "), formatar_bps(resultado.get("premio_anbima")) if resultado.get("premio_anbima") is not None else "-"]))
    
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Posição", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Quantidade: "), formatar_numero_brasileiro(resultado.get("quantidade"), 0) if resultado.get("quantidade") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Financeiro: "), formatar_numero_brasileiro(resultado.get("financeiro"), 2) if resultado.get("financeiro") is not None else "-"]))
    
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Preços Unitários", className="mb-2"))
    resultado_items.append(html.P([html.Strong("PU D0: "), formatar_pu_brasileiro(resultado.get("pu_d0")) if resultado.get("pu_d0") is not None else "-"]))
    resultado_items.append(html.P([html.Strong(f"PU D{dias_liquidacao}: "), formatar_pu_brasileiro(resultado.get("pu_termo")) if resultado.get("pu_termo") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("PU Carregado: "), formatar_pu_brasileiro(resultado.get("pu_carregado")) if resultado.get("pu_carregado") is not None else "-"]))
    
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Sensibilidade e Carregamento", className="mb-2"))
    resultado_items.append(html.P([html.Strong("DV01: "), formatar_dv01(resultado.get("dv01")) if resultado.get("dv01") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Carregamento BRL: "), formatar_numero_brasileiro(resultado.get("carrego_brl"), 2) if resultado.get("carrego_brl") is not None else "-"]))
    resultado_items.append(html.P([html.Strong("Carregamento BPS: "), formatar_bps(resultado.get("carrego_bps")) if resultado.get("carrego_bps") is not None else "-"]))
    
    resultado_items.append(html.Hr(className="my-3"))
    resultado_items.append(html.H5("Hedge DI", className="mb-2"))
    resultado_items.append(html.P([html.Strong("Hedge DI: "), formatar_inteiro(resultado.get("hedge_di")) if resultado.get("hedge_di") is not None else "-"]))
    
    return html.Div(
        resultado_items,
        className="mt-3 p-3 bg-light rounded",
        style={"maxHeight": "600px", "overflowY": "auto"},
    )
