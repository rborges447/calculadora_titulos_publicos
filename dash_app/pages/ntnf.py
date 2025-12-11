"""
Página NTNF - tabela editável usando carteiras.
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from dash_app.utils.carteiras import criar_carteira, atualizar_taxa, atualizar_premio_di, atualizar_dias_liquidacao
from dash_app.utils.vencimentos import formatar_data_para_exibicao
from dash_app.utils.formatacao import formatar_taxa_brasileira, formatar_pu_brasileiro, parse_numero_brasileiro


def layout():
    return dbc.Container(
        [
            dcc.Store(id="ntnf-carteira-id", data=None),
            dcc.Store(id="ntnf-dados-originais", data=[]),
            html.H2("NTNF - Nota do Tesouro Nacional - Série F"),
            html.P("Edite as taxas na tabela para calcular os PU termo de cada vencimento."),
            
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Parâmetros", className="mb-3"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Dias para liquidação"),
                                        dbc.Input(
                                            id="ntnf-dias",
                                            type="number",
                                            value=1,
                                            min=0,
                                        ),
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Tipo de entrada"),
                                        dbc.RadioItems(
                                            id="ntnf-tipo",
                                            options=[
                                                {"label": "Taxa (%)", "value": "taxa"},
                                                {"label": "Prêmio + DI", "value": "premio_di"},
                                            ],
                                            value="taxa",
                                            inline=True,
                                        ),
                                    ],
                                    md=8,
                                ),
                            ],
                            className="mb-3",
                        ),
                        html.Div(
                            [
                                dbc.Label("DI (%) - usado quando tipo = Prêmio + DI"),
                                dbc.Input(
                                    id="ntnf-di",
                                    type="number",
                                    value=0.0,
                                    step=0.01,
                                ),
                            ],
                            id="ntnf-box-di",
                            style={"display": "none"},
                        ),
                    ]
                ),
                className="mb-4",
            ),
            
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Tabela de Vencimentos", className="mb-3"),
                        html.Div(id="ntnf-tabela-container"),
                    ]
                ),
            ),
        ],
        fluid=True,
        className="py-2",
    )


@callback(
    [
        Output("ntnf-carteira-id", "data"),
        Output("ntnf-dados-originais", "data"),
        Output("ntnf-tabela-container", "children"),
    ],
    [
        Input("ntnf-dias", "value"),
    ],
    State("ntnf-carteira-id", "data"),
    prevent_initial_call=False,
)
def carregar_carteira(dias, carteira_id_existente):
    """Carrega ou atualiza a carteira"""
    try:
        # Permitir 0 como valor válido (dias or 1 trataria 0 como False)
        dias = dias if dias is not None else 1
        
        # Se já existe uma carteira, atualizar os dias de liquidação
        if carteira_id_existente:
            print(f"[INFO] Atualizando dias de liquidação para {dias} na carteira existente...")
            ok, resultado = atualizar_dias_liquidacao("ntnf", carteira_id_existente, dias)
            if ok:
                carteira_id = carteira_id_existente
            else:
                # Se falhou (ex: carteira não existe mais), criar nova
                print(f"[INFO] Falha ao atualizar dias, criando nova carteira...")
                ok, resultado = criar_carteira("ntnf", dias_liquidacao=dias)
                if not ok:
                    return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
                carteira_id = resultado.get("carteira_id")
        else:
            # Criar nova carteira
            print(f"[INFO] Criando nova carteira com {dias} dias de liquidação...")
            ok, resultado = criar_carteira("ntnf", dias_liquidacao=dias)
            if not ok:
                return None, [], html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
            carteira_id = resultado.get("carteira_id")
        
        dados = [
            {
                "vencimento": formatar_data_para_exibicao(t["vencimento"]),
                "vencimento_raw": t["vencimento"],
                "taxa": formatar_taxa_brasileira(t.get("taxa")) if t.get("taxa") else "",
                "pu_termo": formatar_pu_brasileiro(t.get("pu_termo")) if t.get("pu_termo") else "",
            }
            for t in resultado["titulos"]
        ]
        
        tabela = dash_table.DataTable(
            id="ntnf-tabela",
            columns=[
                {"name": "Vencimento", "id": "vencimento", "editable": False},
                {"name": "Taxa (%)", "id": "taxa", "editable": True, "type": "text"},
                {"name": "PU Termo", "id": "pu_termo", "editable": False, "type": "text"},
            ],
            data=dados,
            editable=True,
            style_cell={"textAlign": "left", "padding": "10px"},
            style_header={"backgroundColor": "#0d6efd", "color": "white", "fontWeight": "bold"},
        )
        
        return carteira_id, dados, tabela
    except Exception as e:
        print(f"[ERRO] Erro ao carregar carteira: {e}")
        import traceback
        traceback.print_exc()
        return None, [], html.P(f"Erro ao carregar carteira: {e}", className="text-danger")


@callback(
    [
        Output("ntnf-tabela", "data", allow_duplicate=True),
        Output("ntnf-carteira-id", "data", allow_duplicate=True),
        Output("ntnf-dados-originais", "data", allow_duplicate=True),
    ],
    [
        Input("ntnf-tabela", "data_timestamp"),
    ],
    [
        State("ntnf-tabela", "data"),
        State("ntnf-tabela", "active_cell"),
        State("ntnf-carteira-id", "data"),
        State("ntnf-dados-originais", "data"),
        State("ntnf-tipo", "value"),
        State("ntnf-di", "value"),
        State("ntnf-dias", "value"),
    ],
    prevent_initial_call=True,
)
def atualizar_taxa_callback(timestamp, data_atual, active_cell, carteira_id, dados_originais, tipo, di, dias):
    """Atualiza taxa quando editada"""
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
            vencimento_exibicao = linha_editada.get("vencimento")
            
            # VALIDAÇÃO: Comparar com dados originais para garantir que estamos na linha certa
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
    
    if not nova_taxa or nova_taxa == "":
        dados_atualizados = [dict(d) for d in data_atual]
        dados_atualizados[row_idx]["pu_termo"] = ""
        dados_originais_atualizados = [dict(d) for d in dados_atualizados]
        return dados_atualizados, carteira_id, dados_originais_atualizados
    
    # Converter do formato brasileiro para float
    taxa_float = parse_numero_brasileiro(nova_taxa)
    if taxa_float is None:
        return data_atual, carteira_id, dados_originais or []
    
    # Tentar atualizar na carteira existente
    if carteira_id:
        if tipo == "taxa":
            ok, resultado = atualizar_taxa("ntnf", carteira_id, vencimento_raw, taxa_float)
        elif tipo == "premio_di" and di:
            ok, resultado = atualizar_premio_di("ntnf", carteira_id, vencimento_raw, taxa_float, float(di))
        else:
            return data_atual, carteira_id, dados_originais or []
        
        if ok:
            titulo = next((t for t in resultado.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, carteira_id, dados_originais_atualizados
    
    # Se falhou ou carteira não existe, recriar
    try:
        ok_criar, resultado_criar = criar_carteira("ntnf", dias_liquidacao=dias if dias is not None else 1)
        if not ok_criar:
            return data_atual, None, dados_originais or []
        
        novo_id = resultado_criar.get("carteira_id")
        
        if tipo == "taxa":
            ok_atualizar, resultado_atualizar = atualizar_taxa("ntnf", novo_id, vencimento_raw, taxa_float)
        elif tipo == "premio_di" and di:
            ok_atualizar, resultado_atualizar = atualizar_premio_di("ntnf", novo_id, vencimento_raw, taxa_float, float(di))
        else:
            return data_atual, novo_id, dados_originais or []
        
        if ok_atualizar:
            titulo = next((t for t in resultado_atualizar.get("titulos", []) if t.get("vencimento") == vencimento_raw), None)
            if titulo:
                dados_atualizados = [dict(d) for d in data_atual]
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, novo_id, dados_originais_atualizados
    except Exception as e:
        print(f"[ERRO] Erro ao recriar carteira: {e}")
    
    return data_atual, carteira_id, dados_originais or []


@callback(
    Output("ntnf-box-di", "style"),
    Input("ntnf-tipo", "value"),
)
def alternar_campos(tipo):
    """Mostra/esconde campo DI"""
    return {"display": "block"} if tipo == "premio_di" else {"display": "none"}
