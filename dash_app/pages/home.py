"""
Página inicial.
"""

from dash import html
import dash_bootstrap_components as dbc


def layout():
    cards = [
        ("LTN", "Cálculo e precificação de LTN.", "/ltn"),
        ("LFT", "Cálculo de LFT com VNA e PU.", "/lft"),
        ("NTNB", "Cálculo e hedge DI da NTNB.", "/ntnb"),
        ("NTNF", "Cálculo de NTNF.", "/ntnf"),
    ]
    card_components = [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(title, className="card-title"),
                            html.P(desc, className="card-text"),
                            dbc.Button("Abrir", color="primary", href=href),
                        ]
                    )
                ],
                className="h-100",
            ),
            md=3,
            sm=6,
            xs=12,
        )
        for title, desc, href in cards
    ]

    return dbc.Container(
        [
            html.H1("Calculadora de Títulos Públicos", className="mb-3"),
            html.P(
                "Interface em Dash para usar a API dos cálculos de LTN, LFT, NTNB e NTNF.",
                className="lead",
            ),
            html.Hr(),
            dbc.Row(card_components, className="gy-3"),
        ],
        fluid=True,
        className="py-3",
    )

