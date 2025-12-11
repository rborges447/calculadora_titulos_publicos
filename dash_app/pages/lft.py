"""
Página LFT - tabela usando carteiras.
"""

from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from dash_app.utils.carteiras import criar_carteira
from dash_app.utils.vencimentos import formatar_data_para_exibicao


def layout():
    return dbc.Container(
        [
            dcc.Store(id="lft-carteira-id", data=None),
            html.H2("LFT - Letra Financeira do Tesouro"),
            html.P("Visualize os PU termo de cada vencimento."),
            
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
                                            id="lft-dias",
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
                        html.Div(id="lft-tabela-container"),
                    ]
                ),
            ),
        ],
        fluid=True,
        className="py-2",
    )


@callback(
    [
        Output("lft-carteira-id", "data"),
        Output("lft-tabela-container", "children"),
    ],
    [
        Input("lft-dias", "value"),
    ],
    State("lft-carteira-id", "data"),
    prevent_initial_call=False,
)
def carregar_carteira(dias, carteira_id_existente):
    """Carrega ou recria a carteira"""
    try:
        # Permitir 0 como valor válido
        dias_valor = dias if dias is not None else 1
        ok, resultado = criar_carteira("lft", dias_liquidacao=dias_valor)
        if not ok:
            return None, html.P(f"Erro ao criar carteira: {resultado.get('error', 'Erro desconhecido')}", className="text-danger")
        
        carteira_id = resultado.get("carteira_id")
        dados = [
            {
                "vencimento": formatar_data_para_exibicao(t["vencimento"]),
                "pu_termo": round(t.get("pu_termo"), 6) if t.get("pu_termo") else "",
            }
            for t in resultado["titulos"]
        ]
        
        tabela = dash_table.DataTable(
            id="lft-tabela",
            columns=[
                {"name": "Vencimento", "id": "vencimento", "editable": False},
                {"name": "PU Termo", "id": "pu_termo", "editable": False, "type": "numeric", "format": {"specifier": ".6f"}},
            ],
            data=dados,
            editable=False,
            style_cell={"textAlign": "left", "padding": "10px"},
            style_header={"backgroundColor": "#0d6efd", "color": "white", "fontWeight": "bold"},
        )
        
        return carteira_id, tabela
    except Exception as e:
        print(f"[ERRO] Erro ao carregar carteira: {e}")
        return None, html.P(f"Erro ao carregar carteira: {e}", className="text-danger")
