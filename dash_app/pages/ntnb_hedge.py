"""
Página NTNB Hedge DI - subpágina de NTNB.
"""

from datetime import date
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

from dash_app.utils.api import post


def layout():
    return dbc.Container(
        [
            html.Div(
                [
                    dcc.Link("← Voltar para NTNB", href="/ntnb", className="text-decoration-none"),
                ],
                className="mb-3",
            ),
            html.H2("NTNB - Hedge DI"),
            html.P("Calcule o hedge DI para NTNB."),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Calcular Hedge DI", className="mb-3"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Data de vencimento NTNB"),
                                        dcc.DatePickerSingle(
                                            id="ntnb-hedge-date",
                                            date=date.today(),
                                            display_format="DD/MM/YYYY",
                                            className="mb-3",
                                        ),
                                        dbc.Label("Código DI (ex: DI1F32)"),
                                        dbc.Input(id="ntnb-hedge-codigo", value="DI1F32", className="mb-3"),
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Taxa (%)"),
                                        dbc.Input(
                                            id="ntnb-hedge-taxa",
                                            type="number",
                                            value=0.0,
                                            step=0.01,
                                            className="mb-3",
                                        ),
                                        dbc.Label("Dias para liquidação"),
                                        dbc.Input(
                                            id="ntnb-hedge-dias",
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
                                        dbc.Label("Quantidade NTNB"),
                                        dbc.Input(
                                            id="ntnb-hedge-quantidade",
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
                                            id="ntnb-hedge-financeiro",
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
                        dbc.Button("Calcular hedge", id="ntnb-hedge-btn", color="primary"),
                    ]
                )
            ),
            html.Div(id="ntnb-hedge-resultado", className="mt-3"),
        ],
        fluid=True,
        className="py-2",
    )


def _resultado_card(res: dict):
    """Exibe resultado do hedge DI em formato de cards."""
    def _fmt(valor, fmt, default="0"):
        try:
            if valor is None:
                valor = default
            return format(valor, fmt) if isinstance(valor, (int, float)) else str(valor)
        except Exception:
            return str(default)

    metrics = [
        ("Quantidade NTNB", _fmt(res.get("quantidade", 0), ",.0f")),
        ("DV01 NTNB", _fmt(res.get("dv01_ntnb", 0), ",.2f")),
        ("Hedge DI", f"{_fmt(res.get('hedge_di', 0), ',.0f')} contratos"),
        ("Ajuste DI", f"{_fmt(res.get('ajuste_di', 0), '.4f')}%"),
    ]

    def _metric_card(label, value):
        return dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(label, className="text-muted"),
                        html.H5(value, className="mb-0"),
                    ]
                ),
                className="h-100 shadow-sm",
            ),
            md=3,
            sm=6,
            xs=12,
        )

    rows = [dbc.Row([_metric_card(lbl, val) for lbl, val in metrics], className="g-3")]

    return dbc.Card(
        [
            dbc.CardHeader("Resultado do Hedge DI"),
            dbc.CardBody(rows),
        ],
        className="mt-3",
    )


@callback(
    Output("ntnb-hedge-resultado", "children"),
    Input("ntnb-hedge-btn", "n_clicks"),
    State("ntnb-hedge-date", "date"),
    State("ntnb-hedge-codigo", "value"),
    State("ntnb-hedge-taxa", "value"),
    State("ntnb-hedge-dias", "value"),
    State("ntnb-hedge-quantidade", "value"),
    State("ntnb-hedge-financeiro", "value"),
    prevent_initial_call=True,
)
def calcular_hedge(n_clicks, data_venc, codigo_di, taxa, dias, quantidade, financeiro):
    if not data_venc:
        return dbc.Alert("Informe a data de vencimento", color="warning")
    if not codigo_di:
        return dbc.Alert("Informe o código DI", color="warning")
    if not financeiro and not quantidade:
        return dbc.Alert("Informe quantidade ou valor financeiro", color="warning")

    payload = {
        "data_vencimento": data_venc,
        "codigo_di": codigo_di,
        "dias_liquidacao": int(dias) if dias else 1,
    }
    if taxa:
        payload["taxa"] = float(taxa)
    if financeiro and financeiro > 0:
        payload["financeiro"] = float(financeiro)
    elif quantidade and quantidade > 0:
        payload["quantidade"] = float(quantidade)

    ok, res = post("/titulos/ntnb/hedge-di", payload)
    if not ok:
        return dbc.Alert(f"Erro: {res}", color="danger")
    return _resultado_card(res)

