"""
Página LTN - cálculo via API.
"""

from datetime import date
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

from dash_app.utils.api import post
from dash_app.utils.vencimentos import get_vencimentos_ltn, formatar_data_para_exibicao


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
                                    id="ltn-date",
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
                                    id="ltn-dias",
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
                                    id="ltn-tipo",
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
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.Label("Taxa (%)"),
                                    dbc.Input(
                                        id="ltn-taxa",
                                        type="number",
                                        value=0.0,
                                        step=0.01,
                                        className="mb-3",
                                    ),
                                ],
                                id="ltn-box-taxa",
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.Label("Prêmio (bps)"),
                                    dbc.Input(
                                        id="ltn-premio",
                                        type="number",
                                        value=0.0,
                                        step=0.1,
                                        className="mb-1",
                                    ),
                                    dbc.Label("DI (%)"),
                                    dbc.Input(
                                        id="ltn-di",
                                        type="number",
                                        value=0.0,
                                        step=0.01,
                                    ),
                                ],
                                id="ltn-box-premio-di",
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
                                    id="ltn-quantidade",
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
                                    id="ltn-financeiro",
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
                dbc.Button("Calcular", id="ltn-btn", color="primary"),
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
                            dbc.Col(
                                [dbc.Label("Quantidade"), html.H5(f"{res.get('quantidade', 0):,.0f}")],
                                md=3,
                            ),
                            dbc.Col(
                                [dbc.Label("Financeiro"), html.H5(f"R$ {res.get('financeiro', 0):,.2f}")],
                                md=3,
                            ),
                            dbc.Col(
                                [dbc.Label("Taxa"), html.H5(f"{res.get('taxa', 0):.4f}%")],
                                md=3,
                            ),
                            dbc.Col(
                                [dbc.Label("PU D0"), html.H5(f"{res.get('pu_d0', 0):.6f}")],
                                md=3,
                            ),
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
            dcc.Store(id="ltn-trigger", data=0),  # Componente para trigger do callback
            html.H2("LTN"),
            html.P("Preencha os campos e envie para calcular via API /titulos/ltn."),
            _form(),
            html.Div(id="ltn-resultado", className="mt-3"),
        ],
        fluid=True,
        className="py-2",
    )


@callback(
    Output("ltn-resultado", "children"),
    Input("ltn-btn", "n_clicks"),
    State("ltn-date", "value"),
    State("ltn-dias", "value"),
    State("ltn-tipo", "value"),
    State("ltn-taxa", "value"),
    State("ltn-premio", "value"),
    State("ltn-di", "value"),
    State("ltn-quantidade", "value"),
    State("ltn-financeiro", "value"),
    prevent_initial_call=True,
)
def calcular(n_clicks, data_venc, dias, tipo, taxa, premio, di, quantidade, financeiro):
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

    ok, res = post("/titulos/ltn", payload)
    if not ok:
        return dbc.Alert(f"Erro: {res}", color="danger")
    return _resultado_card(res)


@callback(
    [
        Output("ltn-box-taxa", "style"),
        Output("ltn-box-premio-di", "style"),
    ],
    Input("ltn-tipo", "value"),
)
def alternar_campos(tipo):
    if tipo == "taxa":
        return {"display": "block"}, {"display": "none"}
    return {"display": "none"}, {"display": "block"}


@callback(
    [Output("ltn-date", "options"), Output("ltn-trigger", "data")],
    Input("ltn-trigger", "data"),
    prevent_initial_call=False,
)
def carregar_vencimentos(_):
    """Carrega lista de vencimentos disponíveis para LTN"""
    try:
        print("[CALLBACK] Carregando vencimentos LTN...")
        vencimentos = get_vencimentos_ltn()
        if not vencimentos:
            print("[WARN] Nenhum vencimento encontrado para LTN")
            return [], 1
        options = [
            {"label": formatar_data_para_exibicao(v), "value": v}
            for v in vencimentos
        ]
        print(f"[OK] Carregados {len(options)} vencimentos LTN no dropdown")
        return options, 1
    except Exception as e:
        print(f"[ERRO] Erro ao carregar vencimentos LTN: {e}")
        import traceback
        traceback.print_exc()
        return [], 1

