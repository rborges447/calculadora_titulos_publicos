"""
Página NTNB - tabela editável usando carteiras.
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from dash_app.utils.carteiras import criar_carteira, atualizar_taxa, atualizar_dias_liquidacao
from dash_app.utils.vencimentos import formatar_data_para_exibicao
from dash_app.utils.formatacao import formatar_taxa_brasileira, formatar_pu_brasileiro, parse_numero_brasileiro


def layout():
    return dbc.Container(
        [
            dcc.Store(id="ntnb-carteira-id", data=None),
            dcc.Store(id="ntnb-dados-originais", data=[]),
            html.H2("NTNB - Nota do Tesouro Nacional - Série B"),
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
                                            id="ntnb-dias",
                                            type="number",
                                            value=1,
                                            min=0,
                                        ),
                                    ],
                                    md=4,
                                ),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
                className="mb-4",
            ),
            
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Tabela de Vencimentos", className="mb-3"),
                        html.Div(id="ntnb-tabela-container"),
                    ]
                ),
            ),
            
            html.Hr(className="my-4"),
            
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Hedge DI", className="mb-3"),
                        html.P("Para calcular o hedge DI, acesse a página dedicada:", className="mb-3"),
                        dcc.Link(
                            "Ir para Hedge DI →",
                            href="/ntnb/hedge-di",
                            style={
                                "display": "inline-block",
                                "padding": "0.5rem 1rem",
                                "background-color": "#6c757d",
                                "color": "white",
                                "border-radius": "0.25rem",
                                "text-decoration": "none",
                                "font-weight": "500",
                            },
                        ),
                    ]
                ),
                className="mt-4",
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
            id="ntnb-tabela",
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
        # Se taxa foi limpa, limpar PU também
        dados_atualizados = [dict(d) for d in data_atual]  # Deep copy
        dados_atualizados[row_idx]["pu_termo"] = ""
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
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)  # Formatar no padrão brasileiro
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
                dados_atualizados[row_idx]["pu_termo"] = formatar_pu_brasileiro(titulo.get("pu_termo")) if titulo.get("pu_termo") else ""
                dados_atualizados[row_idx]["taxa"] = formatar_taxa_brasileira(taxa_float)
                dados_originais_atualizados = [dict(d) for d in dados_atualizados]
                return dados_atualizados, novo_id, dados_originais_atualizados
    except Exception as e:
        # Log de erro apenas se necessário (sem print de debug)
        pass
    
    return data_atual, carteira_id, dados_originais or []
