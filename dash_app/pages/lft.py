"""
Página LFT - cálculo via API.
"""

from datetime import date
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

from dash_app.utils.api import post


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
                                dcc.DatePickerSingle(
                                    id="lft-date",
                                    date=date.today(),
                                    display_format="DD/MM/YYYY",
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dias para liquidação"),
                                dbc.Input(
                                    id="lft-dias",
                                    type="number",
                                    value=1,
                                    min=0,
                                    className="mb-3",
                                ),
                            ],
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
                                    id="lft-quantidade",
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
                                    id="lft-financeiro",
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
                dbc.Button("Calcular", id="lft-btn", color="primary"),
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
                            dbc.Col([dbc.Label("PU D0"), html.H5(f"{res.get('pu_d0', 0):.6f}")], md=3),
                            dbc.Col([dbc.Label("VNA"), html.H5(f"R$ {res.get('vna', 0):,.6f}")], md=3),
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
            html.H2("LFT"),
            html.P("Preencha os campos e envie para calcular via API /titulos/lft."),
            _form(),
            html.Div(id="lft-resultado", className="mt-3"),
        ],
        fluid=True,
        className="py-2",
    )


@callback(
    Output("lft-resultado", "children"),
    Input("lft-btn", "n_clicks"),
    State("lft-date", "date"),
    State("lft-dias", "value"),
    State("lft-quantidade", "value"),
    State("lft-financeiro", "value"),
    prevent_initial_call=True,
)
def calcular(n_clicks, data_venc, dias, quantidade, financeiro):
    if not data_venc:
        return dbc.Alert("Informe a data de vencimento", color="warning")
    if not financeiro and not quantidade:
        return dbc.Alert("Informe quantidade ou valor financeiro", color="warning")

    payload = {"data_vencimento": data_venc, "dias_liquidacao": int(dias) if dias else 1}
    if financeiro and financeiro > 0:
        payload["financeiro"] = float(financeiro)
    elif quantidade and quantidade > 0:
        payload["quantidade"] = float(quantidade)

    ok, res = post("/titulos/lft", payload)
    if not ok:
        return dbc.Alert(f"Erro: {res}", color="danger")
    return _resultado_card(res)

