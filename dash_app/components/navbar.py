"""
Navbar simples para navegação entre páginas.
"""

import dash_bootstrap_components as dbc
from dash import html

from dash_app import config


def Navbar():
    links = [
        dbc.NavItem(dbc.NavLink(info["label"], href=info["path"], active="exact"))
        for info in config.PAGES.values()
    ]

    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(config.APP_TITLE, href="/", className="fw-bold"),
                dbc.Nav(links, className="ms-auto", pills=True),
            ],
            fluid=True,
        ),
        color="light",
        light=True,
        className="shadow-sm",
    )

