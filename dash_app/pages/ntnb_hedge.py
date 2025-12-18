"""
Página NTNB Hedge DI - subpágina de NTNB.
"""

from datetime import date
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

from dash_app.utils.api import post
from dash_app.utils.vencimentos import (
    get_vencimentos_ntnb,
    get_codigos_di,
    formatar_data_para_exibicao,
)
from dash_app.utils.formatacao import formatar_numero_brasileiro, parse_numero_brasileiro


def layout():
    return dbc.Container(
        [
            dcc.Store(id="ntnb-hedge-trigger", data=0),
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
                                        dcc.Dropdown(
                                            id="ntnb-hedge-date",
                                            options=[],
                                            placeholder="Selecione o vencimento...",
                                            className="mb-3",
                                        ),
                                        dbc.Label("Código DI"),
                                        dcc.Dropdown(
                                            id="ntnb-hedge-codigo",
                                            options=[],
                                            placeholder="Selecione o código DI...",
                                            className="mb-3",
                                        ),
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
    def _fmt_brasileiro(valor, casas_decimais=0, default="0"):
        try:
            if valor is None:
                return default
            return formatar_numero_brasileiro(float(valor), casas_decimais) if isinstance(valor, (int, float)) else str(valor)
        except Exception:
            return str(default)

    metrics = [
        ("Quantidade NTNB", _fmt_brasileiro(res.get("quantidade", 0), 0)),
        ("DV01 NTNB", _fmt_brasileiro(res.get("dv01_ntnb", 0), 2)),
        ("Hedge DI", f"{_fmt_brasileiro(res.get('hedge_di', 0), 0)} contratos"),
        ("Ajuste DI", f"{_fmt_brasileiro(res.get('ajuste_di', 0), 4)}%"),
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
    State("ntnb-hedge-date", "value"),
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
        "dias_liquidacao": int(dias) if dias is not None else 1,
    }
    if taxa:
        # Converter do formato brasileiro se necessário
        taxa_float = parse_numero_brasileiro(str(taxa)) if isinstance(taxa, str) else float(taxa)
        if taxa_float is not None:
            payload["taxa"] = taxa_float
    if financeiro and financeiro > 0:
        # Converter do formato brasileiro se necessário
        financeiro_float = parse_numero_brasileiro(str(financeiro)) if isinstance(financeiro, str) else float(financeiro)
        if financeiro_float is not None:
            payload["financeiro"] = financeiro_float
    elif quantidade and quantidade > 0:
        # Converter do formato brasileiro se necessário
        quantidade_float = parse_numero_brasileiro(str(quantidade)) if isinstance(quantidade, str) else float(quantidade)
        if quantidade_float is not None:
            payload["quantidade"] = quantidade_float

    ok, res = post("/titulos/ntnb/hedge-di", payload)
    if not ok:
        return dbc.Alert(f"Erro: {res}", color="danger")
    return _resultado_card(res)


@callback(
    [
        Output("ntnb-hedge-date", "options"),
        Output("ntnb-hedge-codigo", "options"),
        Output("ntnb-hedge-trigger", "data"),
    ],
    Input("ntnb-hedge-trigger", "data"),
    prevent_initial_call=False,
)
def carregar_dados_hedge(_):
    """Carrega lista de vencimentos e códigos DI disponíveis"""
    try:
        vencimentos = get_vencimentos_ntnb()
        codigos = get_codigos_di()
        
        options_vencimentos = [
            {"label": formatar_data_para_exibicao(v), "value": v}
            for v in vencimentos
        ] if vencimentos else []
        
        options_codigos = [
            {"label": codigo, "value": codigo} for codigo in codigos
        ] if codigos else []
        
        return options_vencimentos, options_codigos, 1
    except Exception as e:
        print(f"❌ Erro ao carregar dados hedge: {e}")
        import traceback
        traceback.print_exc()
        return [], [], 1

