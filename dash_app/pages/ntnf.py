"""
Página NTNF - cálculo via API.
"""

from datetime import date
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

from dash_app.utils.api import post
from dash_app.utils.vencimentos import get_vencimentos_ntnf, formatar_data_para_exibicao


def _form():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Parâmetros", className="mb-3"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Data de vencimento"),
                                dcc.Dropdown(
                                    id="ntnf-date",
                                    options=[],
                                    placeholder="Selecione o vencimento...",
                                    className="mb-3",
                                ),
                            ],
                            md=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dias para liquidação"),
                                dbc.Input(
                                    id="ntnf-dias",
                                    type="number",
                                    value=1,
                                    min=0,
                                    className="mb-3",
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
                            md=4,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.Label("Taxa (%)"),
                                    dbc.Input(
                                        id="ntnf-taxa",
                                        type="number",
                                        value=0.0,
                                        step=0.01,
                                        className="mb-3",
                                    ),
                                ],
                                id="ntnf-box-taxa",
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.Label("Prêmio (bps)"),
                                    dbc.Input(
                                        id="ntnf-premio",
                                        type="number",
                                        value=0.0,
                                        step=0.1,
                                        className="mb-1",
                                    ),
                                    dbc.Label("DI (%)"),
                                    dbc.Input(
                                        id="ntnf-di",
                                        type="number",
                                        value=0.0,
                                        step=0.01,
                                    ),
                                ],
                                id="ntnf-box-premio-di",
                                style={"display": "none"},
                            ),
                            md=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Quantidade"),
                                dbc.Input(
                                    id="ntnf-quantidade",
                                    type="number",
                                    value=0.0,
                                    step=1,
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Valor financeiro (R$)"),
                                dbc.Input(
                                    id="ntnf-financeiro",
                                    type="number",
                                    value=0.0,
                                    step=1000,
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                    ]
                ),
                dbc.Button("Calcular", id="ntnf-btn", color="primary"),
            ]
        )
    )


def _resultado_card(res: dict):
    return dbc.Card(
        [
            dbc.CardHeader("Resultado do cálculo"),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col([dbc.Label("Quantidade"), html.H5(f"{res.get('quantidade', 0):,.0f}")], md=3),
                            dbc.Col([dbc.Label("Financeiro"), html.H5(f"R$ {res.get('financeiro', 0):,.2f}")], md=3),
                            dbc.Col([dbc.Label("Taxa"), html.H5(f"{res.get('taxa', 0):.4f}%")], md=3),
                            dbc.Col([dbc.Label("PU D0"), html.H5(f"{res.get('pu_d0', 0):.6f}")], md=3),
                        ],
                        className="gy-2",
                    ),
                    html.Pre(str(res), className="result-pre mt-3"),
                ]
            ),
        ],
        className="mt-3",
    )


def layout():
    return dbc.Container(
        [
            dcc.Store(id="ntnf-trigger", data=0),
            html.H2("NTNF"),
            html.P("Preencha os campos e envie para calcular via API /titulos/ntnf."),
            _form(),
            html.Div(id="ntnf-resultado", className="mt-3"),
        ],
        fluid=True,
        className="py-2",
    )


@callback(
    Output("ntnf-resultado", "children"),
    Input("ntnf-btn", "n_clicks"),
    State("ntnf-date", "value"),
    State("ntnf-dias", "value"),
    State("ntnf-tipo", "value"),
    State("ntnf-taxa", "value"),
    State("ntnf-premio", "value"),
    State("ntnf-di", "value"),
    State("ntnf-quantidade", "value"),
    State("ntnf-financeiro", "value"),
    prevent_initial_call=True,
)
def calcular_ntnf(n_clicks, data_venc, dias, tipo, taxa, premio, di, quantidade, financeiro):
    if not data_venc:
        return dbc.Alert("Informe a data de vencimento", color="warning")
    if not financeiro and not quantidade:
        return dbc.Alert("Informe quantidade ou valor financeiro", color="warning")

    payload = {"data_vencimento": data_venc, "dias_liquidacao": int(dias) if dias else 1}
    if tipo == "taxa":
        if taxa:
            payload["taxa"] = float(taxa)
    else:
        if premio:
            payload["premio"] = float(premio)
        if di:
            payload["di"] = float(di)

    if financeiro and financeiro > 0:
        payload["financeiro"] = float(financeiro)
    elif quantidade and quantidade > 0:
        payload["quantidade"] = float(quantidade)

    ok, res = post("/titulos/ntnf", payload)
    if not ok:
        return dbc.Alert(f"Erro: {res}", color="danger")
    return _resultado_card(res)


@callback(
    [
        Output("ntnf-box-taxa", "style"),
        Output("ntnf-box-premio-di", "style"),
    ],
    Input("ntnf-tipo", "value"),
)
def alternar_campos(tipo):
    if tipo == "taxa":
        return {"display": "block"}, {"display": "none"}
    return {"display": "none"}, {"display": "block"}


@callback(
    [Output("ntnf-date", "options"), Output("ntnf-trigger", "data")],
    Input("ntnf-trigger", "data"),
    prevent_initial_call=False,
)
def carregar_vencimentos_ntnf(_):
    """Carrega lista de vencimentos disponíveis para NTNF"""
    try:
        vencimentos = get_vencimentos_ntnf()
        if not vencimentos:
            return [], 1
        options = [
            {"label": formatar_data_para_exibicao(v), "value": v}
            for v in vencimentos
        ]
        return options, 1
    except Exception as e:
        print(f"❌ Erro ao carregar vencimentos NTNF: {e}")
        return [], 1

