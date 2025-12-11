"""
Aplicação Dash (reconstruída) - Calculadora de Títulos Públicos.
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from dash_app import config
from dash_app.components.navbar import Navbar
from dash_app.pages import home, ltn, lft, ntnb, ntnb_hedge, ntnf


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    title=config.APP_TITLE,
)

# CSS básico para legibilidade em tema claro
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { background-color: #f6f8fb; color: #0f172a; }
            .card { border-radius: 8px; }
            .form-label { font-weight: 600; }
            .result-pre { white-space: pre-wrap; font-size: 12px; background: #0f172a; color: #e5e7eb; padding: 12px; border-radius: 6px; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        Navbar(),
        dbc.Container(id="page-content", fluid=True, className="py-4"),
    ]
)


@app.callback(
    dash.Output("page-content", "children"),
    dash.Input("url", "pathname"),
)
def render_page(pathname: str):
    if pathname in ("/", "/home", None):
        return home.layout()
    if pathname == "/ltn":
        return ltn.layout()
    if pathname == "/lft":
        return lft.layout()
    if pathname == "/ntnb":
        return ntnb.layout()
    if pathname == "/ntnb/hedge-di":
        return ntnb_hedge.layout()
    if pathname == "/ntnf":
        return ntnf.layout()
    return home.layout()


if __name__ == "__main__":
    app.run(debug=True, port=8050, host="127.0.0.1")

