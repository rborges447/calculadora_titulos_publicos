"""
Página NTNB - cálculo e hedge via API.
"""

from datetime import date
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

from dash_app.utils.api import post
from dash_app.utils.vencimentos import get_vencimentos_ntnb, formatar_data_para_exibicao


def _form_calculo():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Calcular NTNB", className="mb-3"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Data de vencimento"),
                                dcc.Dropdown(
                                    id="ntnb-date",
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
                                    id="ntnb-dias",
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
                                dbc.Label("Taxa (%)"),
                                dbc.Input(
                                    id="ntnb-taxa",
                                    type="number",
                                    value=0.0,
                                    step=0.01,
                                    className="mb-3",
                                ),
                            ],
                            md=4,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Quantidade"),
                                dbc.Input(
                                    id="ntnb-quantidade",
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
                                    id="ntnb-financeiro",
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
                dbc.Button("Calcular", id="ntnb-btn", color="primary"),
            ]
        )
    )


def _resultado_card(res: dict, titulo: str):
    dias_liq = res.get("dias_liquidacao") or res.get("dias_liq") or 1
    label_pu_termo = f"PU D{dias_liq}"
    label_cotacao = f"Cotação D{dias_liq}"

    def _fmt(valor, fmt, default="0"):
        try:
            if valor is None:
                valor = default
            return format(valor, fmt) if isinstance(valor, (int, float)) else str(valor)
        except Exception:
            return str(default)

    metrics = [
        ("Data de Liquidação", res.get("data_liquidacao", "-")),
        ("Quantidade", _fmt(res.get("quantidade", 0), ",.0f")),
        ("Financeiro", f"R$ {_fmt(res.get('financeiro', 0), ',.2f')}"),
        ("Taxa", f"{_fmt(res.get('taxa', 0), '.4f')}%"),
        ("PU D0", _fmt(res.get("pu_d0", 0), ".6f")),
        (label_pu_termo, _fmt(res.get("pu_termo", 0), ".6f")),
        (label_cotacao, _fmt(res.get("cotacao", 0), ".6f")),
        ("PU Carregado", _fmt(res.get("pu_carregado", 0), ".6f")),
        ("DV01 BRL", _fmt(res.get("dv01", 0), ",.2f")),
        ("Carrego BRL", f"R$ {_fmt(res.get('carrego_brl', 0), ',.2f')}"),
        ("Carrego BPS", _fmt(res.get("carrego_bps", 0), ".2f")),
        ("Hedge DAP", _fmt(res.get("hedge_dap", 0), ",.0f")),
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

    # Distribuir em linhas de 4 colunas no desktop
    rows = []
    for i in range(0, len(metrics), 4):
        chunk = metrics[i : i + 4]
        rows.append(dbc.Row([_metric_card(lbl, val) for lbl, val in chunk], className="g-3"))

    return dbc.Card(
        [
            dbc.CardHeader(titulo),
            dbc.CardBody(rows),
        ],
        className="mt-3",
    )


def layout():
    return dbc.Container(
        [
            dcc.Store(id="ntnb-trigger", data=0),
            html.H2("NTNB"),
            html.P("Calcule NTNB consumindo a API."),
            _form_calculo(),
            html.Div(id="ntnb-resultado", className="mt-3"),
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
    Output("ntnb-resultado", "children"),
    Input("ntnb-btn", "n_clicks"),
    State("ntnb-date", "value"),
    State("ntnb-dias", "value"),
    State("ntnb-taxa", "value"),
    State("ntnb-quantidade", "value"),
    State("ntnb-financeiro", "value"),
    prevent_initial_call=True,
)
def calcular_ntnb(n_clicks, data_venc, dias, taxa, quantidade, financeiro):
    if not data_venc:
        return dbc.Alert("Informe a data de vencimento", color="warning")
    if not financeiro and not quantidade:
        return dbc.Alert("Informe quantidade ou valor financeiro", color="warning")

    payload = {"data_vencimento": data_venc, "dias_liquidacao": int(dias) if dias else 1}
    if taxa:
        payload["taxa"] = float(taxa)

    if financeiro and financeiro > 0:
        payload["financeiro"] = float(financeiro)
    elif quantidade and quantidade > 0:
        payload["quantidade"] = float(quantidade)

    ok, res = post("/titulos/ntnb", payload)
    if not ok:
        return dbc.Alert(f"Erro: {res}", color="danger")
    return _resultado_card(res, "Resultado do cálculo")


@callback(
    [Output("ntnb-date", "options"), Output("ntnb-trigger", "data")],
    Input("ntnb-trigger", "data"),
    prevent_initial_call=False,
)
def carregar_vencimentos_ntnb(_):
    """Carrega lista de vencimentos disponíveis para NTNB"""
    try:
        vencimentos = get_vencimentos_ntnb()
        if not vencimentos:
            return [], 1
        options = [
            {"label": formatar_data_para_exibicao(v), "value": v}
            for v in vencimentos
        ]
        return options, 1
    except Exception as e:
        print(f"❌ Erro ao carregar vencimentos NTNB: {e}")
        return [], 1



