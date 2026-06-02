"""

Página Consultas DB — explorer do gold bbdb via API (Spec 003).

"""



from __future__ import annotations



import base64

from datetime import date, datetime, timedelta
from typing import Any



import dash

import dash_bootstrap_components as dbc

import dash_table

from dash import Input, Output, State, callback, dcc, html, no_update



from dash_app.utils.api import CONSULTAS_DB_TIMEOUT, get, post, post_bytes

from dash_app.utils.formatacao_pt_br import (

    formatar_inteiro_pt_br,

    formatar_rows_para_exibicao,

)



_TABELAS_ALTO_VOLUME = frozenset({

    "mercado_secundario",

    "liquidacoes_mercado",

    "mercado_com_liquidacoes",

})



_PREVIEW_OCULTO = {"display": "none"}





def layout():

    return dbc.Container(

        [

            dcc.Store(id="consultas-db-init", data=0),

            dcc.Store(id="consultas-db-catalogo-store"),

            dcc.Store(id="consultas-db-resultado-store"),

            html.H2("Consultas ao banco"),

            html.P(

                "Explore o histórico persistido no SQLite gold (bbdb): "

                "escolha tabela, colunas e período. Dados brutos — sem cálculo de título.",

                className="text-muted mb-3",

            ),

            dbc.Alert(

                id="consultas-db-status-banner",

                is_open=False,

                color="warning",

                className="mb-3",

            ),

            dbc.Card(

                dbc.CardBody(

                    [

                        dbc.Row(

                            [

                                dbc.Col(

                                    [

                                        dbc.Label("Tabela"),

                                        dcc.Dropdown(

                                            id="consultas-db-tabela",

                                            placeholder="Carregando catálogo...",

                                            className="mb-2",

                                        ),

                                        html.Small(

                                            id="consultas-db-descricao",

                                            className="text-muted",

                                        ),

                                    ],

                                    md=6,

                                ),

                                dbc.Col(

                                    [

                                        dbc.Label("Colunas"),

                                        dbc.Checklist(

                                            id="consultas-db-colunas",

                                            options=[],

                                            value=[],

                                            inline=False,

                                            className="mb-2",

                                        ),

                                    ],

                                    md=6,

                                ),

                            ]

                        ),

                        html.Div(

                            [

                                dbc.Label("Período"),

                                dcc.DatePickerRange(

                                    id="consultas-db-datas",

                                    display_format="DD/MM/YYYY",

                                    className="mb-2",

                                ),

                            ],

                            id="consultas-db-datas-wrap",

                            className="mb-2",

                        ),

                        dbc.ButtonGroup(

                            [

                                dbc.Button(

                                    "Consultar",

                                    id="consultas-db-btn-consultar",

                                    color="primary",

                                ),

                                dbc.Button(

                                    "Baixar CSV",

                                    id="consultas-db-btn-csv",

                                    color="secondary",

                                    outline=True,

                                ),

                            ],

                            className="mb-2",

                        ),

                        dcc.Download(id="consultas-db-download"),

                    ]

                ),

                className="mb-3",

            ),

            dbc.Alert(

                id="consultas-db-alerta",

                is_open=False,

                dismissable=True,

                className="mb-3",

            ),

            html.Div(id="consultas-db-meta", className="mb-2 text-muted small"),

            html.Div(

                [

                    dbc.Label("Colunas visíveis no preview"),

                    dbc.Checklist(

                        id="consultas-db-colunas-preview",

                        options=[],

                        value=[],

                        inline=True,

                        className="mb-1",

                    ),

                    html.Small(

                        "Filtros e colunas ocultas valem só para o preview. "

                        "O CSV reflete a consulta completa (tabela, colunas e período "

                        "selecionados acima).",

                        className="text-muted d-block mb-2",

                    ),

                ],

                id="consultas-db-preview-tools",

                style=_PREVIEW_OCULTO,

            ),

            html.Div(id="consultas-db-tabela-container"),

        ],

        fluid=True,

        className="py-2",

    )





def _format_date(value: Any) -> str | None:

    if value is None:

        return None

    if isinstance(value, datetime):

        return value.date().isoformat()

    if isinstance(value, date):

        return value.isoformat()

    if isinstance(value, (int, float)):

        ts = float(value)

        if ts > 1e12:

            ts /= 1000.0

        return datetime.fromtimestamp(ts).date().isoformat()

    if isinstance(value, str):

        s = value.strip()

        if not s:

            return None

        if "/" in s:

            parte = s.split(" ", 1)[0]

            try:

                dia, mes, ano = (int(x) for x in parte.split("/")[:3])

                return date(ano, mes, dia).isoformat()

            except (ValueError, TypeError):

                pass

        return s[:10] if len(s) >= 10 else None

    return None


def _intervalo_padrao_fonte(disp_ini: str, disp_fim: str, *, max_dias: int = 30) -> tuple[str, str]:

    ini = date.fromisoformat(disp_ini)

    fim = date.fromisoformat(disp_fim)

    if (fim - ini).days <= max_dias:

        return disp_ini, disp_fim

    inicio = fim - timedelta(days=max_dias)

    if inicio < ini:

        inicio = ini

    return inicio.isoformat(), fim.isoformat()





def _formatar_data_ui(iso: str) -> str:

    try:

        d = date.fromisoformat(iso[:10])

        return d.strftime("%d/%m/%Y")

    except ValueError:

        return iso


def _fonte_por_id(fontes: list[dict], tabela_id: str | None) -> dict | None:

    if not tabela_id or not fontes:

        return None

    for fonte in fontes:

        if fonte.get("id") == tabela_id:

            return fonte

    return None





def _mostra_datas(fonte: dict | None) -> bool:

    if fonte is None:

        return True

    if fonte.get("modo") == "range":

        return True

    return fonte.get("coluna_data") is not None





def _build_payload(

    tabela_id: str | None,

    colunas: list[str] | None,

    start_date: Any,

    end_date: Any,

    fonte: dict | None,

) -> tuple[dict | None, str | None]:

    if not tabela_id:

        return None, "Selecione uma tabela."

    if not colunas:

        return None, "Selecione ao menos uma coluna."



    data_inicio = _format_date(start_date)

    data_fim = _format_date(end_date)

    if fonte and fonte.get("modo") == "range":

        if not data_inicio or not data_fim:

            disp_ini = fonte.get("data_disponivel_inicio")

            disp_fim = fonte.get("data_disponivel_fim")

            if disp_ini and disp_fim:

                return None, (
                    f"Selecione um período entre {_formatar_data_ui(disp_ini)} e "
                    f"{_formatar_data_ui(disp_fim)}. "
                    "Datas fora desse intervalo não são aceitas pelo seletor."
                )

            return None, "Informe data inicial e final para tabelas em modo range."

        if data_inicio > data_fim:

            return None, "Data inicial deve ser anterior ou igual à data final."



    return {

        "tabela": tabela_id,

        "colunas": list(colunas),

        "data_inicio": data_inicio,

        "data_fim": data_fim,

    }, None





def _aviso_volume(tabela_id: str | None, data_inicio: str | None, data_fim: str | None) -> str | None:

    if tabela_id not in _TABELAS_ALTO_VOLUME or not data_inicio or not data_fim:

        return None

    try:

        inicio = date.fromisoformat(data_inicio)

        fim = date.fromisoformat(data_fim)

        dias = (fim - inicio).days

        if dias > 30:

            return (

                f"Atenção: intervalo de {dias} dias em '{tabela_id}' pode gerar "

                "consulta lenta e grande volume de dados."

            )

    except ValueError:

        pass

    return None





def _colunas_ocultas(colunas: list[str], visiveis: list[str]) -> list[str]:

    visiveis_set = set(visiveis)

    return [c for c in colunas if c not in visiveis_set]





def _montar_datatable(

    colunas: list[str],

    rows: list[dict],

    *,

    hidden_columns: list[str] | None = None,

) -> dash_table.DataTable:

    return dash_table.DataTable(

        id="consultas-db-datatable",

        columns=[{"name": c, "id": c} for c in colunas],

        data=rows,

        filter_action="native",

        filter_options={"case": "insensitive"},

        sort_action="native",

        sort_mode="multi",

        hidden_columns=hidden_columns or [],

        editable=False,

        style_cell={

            "textAlign": "left",

            "padding": "5px",

            "fontSize": "11px",

            "whiteSpace": "normal",

            "height": "auto",

            "minWidth": "80px",

        },

        style_header={

            "backgroundColor": "#0d6efd",

            "color": "white",

            "fontWeight": "bold",

            "fontSize": "11px",

        },

        style_table={

            "overflowX": "auto",

            "overflowY": "auto",

            "maxHeight": "500px",

            "width": "100%",

        },

        fixed_rows={"headers": True},

        page_size=25,

        virtualization=True,

    )





def _resposta_consulta_vazia(

    alerta: Any = "",

    alerta_aberto: bool = False,

    alerta_cor: str = "danger",

    meta: str = "",

) -> tuple:

    return (

        None,

        _PREVIEW_OCULTO,

        [],

        [],

        alerta,

        alerta_aberto,

        alerta_cor,

        meta,

        "",

    )





@callback(

    Output("consultas-db-catalogo-store", "data"),

    Output("consultas-db-status-banner", "children"),

    Output("consultas-db-status-banner", "is_open"),

    Output("consultas-db-status-banner", "color"),

    Output("consultas-db-tabela", "options"),

    Output("consultas-db-tabela", "value"),

    Input("consultas-db-init", "data"),

    prevent_initial_call=False,

)

def carregar_catalogo_e_status(_trigger):

    ok_cat, cat_result = get("/consultas-db/catalogo", timeout=30)

    if not ok_cat:

        return (

            [],

            f"Não foi possível carregar o catálogo: {cat_result}",

            True,

            "danger",

            [],

            None,

        )



    fontes = cat_result.get("fontes", [])

    options = [{"label": f["rotulo"], "value": f["id"]} for f in fontes]

    primeira = fontes[0]["id"] if fontes else None



    banner_children = ""

    banner_open = False

    banner_color = "warning"



    ok_status, status_result = get("/consultas-db/status", timeout=15)

    if ok_status and not status_result.get("db_existe", False):

        path = status_result.get("db_path", "")

        banner_children = (

            f"Banco SQLite não encontrado em {path}. "

            "Configure BBDB_DB_PATH e materialize o banco com bbdb.update."

        )

        banner_open = True

    elif not ok_status:

        banner_children = f"Não foi possível verificar o status do banco: {status_result}"

        banner_open = True

        banner_color = "danger"



    return fontes, banner_children, banner_open, banner_color, options, primeira





@callback(

    Output("consultas-db-colunas", "options"),

    Output("consultas-db-colunas", "value"),

    Output("consultas-db-datas-wrap", "style"),

    Output("consultas-db-descricao", "children"),

    Output("consultas-db-datas", "min_date_allowed"),

    Output("consultas-db-datas", "max_date_allowed"),

    Output("consultas-db-datas", "start_date"),

    Output("consultas-db-datas", "end_date"),

    Input("consultas-db-tabela", "value"),

    State("consultas-db-catalogo-store", "data"),

)

def atualizar_colunas_e_datas(tabela_id, fontes):

    fonte = _fonte_por_id(fontes or [], tabela_id)

    if fonte is None:

        return [], [], {"display": "none"}, "", None, None, None, None



    options = [{"label": c, "value": c} for c in fonte.get("colunas", [])]

    value = list(fonte.get("colunas_padrao", []))

    style = {} if _mostra_datas(fonte) else {"display": "none"}

    desc_parts = [fonte.get("descricao") or ""]

    disp_ini = fonte.get("data_disponivel_inicio")

    disp_fim = fonte.get("data_disponivel_fim")

    if disp_ini and disp_fim:

        desc_parts.append(
            f"Dados no banco: {_formatar_data_ui(disp_ini)} a {_formatar_data_ui(disp_fim)}."
        )

    descricao = " ".join(p for p in desc_parts if p).strip()

    start_date = end_date = None

    if _mostra_datas(fonte) and disp_ini and disp_fim:

        start_date, end_date = _intervalo_padrao_fonte(disp_ini, disp_fim)

    return options, value, style, descricao, disp_ini, disp_fim, start_date, end_date





@callback(

    Output("consultas-db-resultado-store", "data"),

    Output("consultas-db-preview-tools", "style"),

    Output("consultas-db-colunas-preview", "options"),

    Output("consultas-db-colunas-preview", "value"),

    Output("consultas-db-alerta", "children"),

    Output("consultas-db-alerta", "is_open"),

    Output("consultas-db-alerta", "color"),

    Output("consultas-db-meta", "children"),

    Output("consultas-db-tabela-container", "children"),

    Input("consultas-db-btn-consultar", "n_clicks"),

    State("consultas-db-tabela", "value"),

    State("consultas-db-colunas", "value"),

    State("consultas-db-datas", "start_date"),

    State("consultas-db-datas", "end_date"),

    State("consultas-db-catalogo-store", "data"),

    prevent_initial_call=True,

)

def consultar_dados(n_clicks, tabela_id, colunas, start_date, end_date, fontes):

    if not n_clicks:

        return (no_update,) * 9



    fonte = _fonte_por_id(fontes or [], tabela_id)

    payload, erro = _build_payload(tabela_id, colunas, start_date, end_date, fonte)

    if erro:

        return _resposta_consulta_vazia(erro, True, "danger")



    alertas: list[Any] = []

    aviso_vol = _aviso_volume(

        tabela_id,

        payload.get("data_inicio"),

        payload.get("data_fim"),

    )

    if aviso_vol:

        alertas.append(dbc.Alert(aviso_vol, color="warning", className="mb-0"))



    ok, resultado = post(

        "/consultas-db/consultar",

        payload,

        timeout=CONSULTAS_DB_TIMEOUT,

    )

    if not ok:

        return _resposta_consulta_vazia(resultado, True, "danger")



    if resultado.get("intervalo_ajustado") and resultado.get("mensagem_aviso"):

        alertas.append(

            dbc.Alert(resultado["mensagem_aviso"], color="warning", className="mb-0")

        )



    if resultado.get("truncado"):

        n_exibidas = len(resultado.get("rows", []))

        n_total = resultado.get("total_linhas", 0)

        alertas.append(

            dbc.Alert(

                f"Preview limitado: exibindo {formatar_inteiro_pt_br(n_exibidas)} de "

                f"{formatar_inteiro_pt_br(n_total)} linhas. "

                "Use Baixar CSV para o recorte completo (até o limite de exportação).",

                color="warning",

                className="mb-0",

            )

        )



    colunas_resp = resultado.get("colunas", [])

    rows = formatar_rows_para_exibicao(colunas_resp, resultado.get("rows", []))

    total = resultado.get("total_linhas", len(rows))

    meta = (

        f"Exibindo {formatar_inteiro_pt_br(len(rows))} de "

        f"{formatar_inteiro_pt_br(total)} linhas."

    )



    alert_children = alertas if alertas else ""

    alert_open = bool(alertas)

    alert_color = "warning" if alertas else "danger"



    if not rows:

        return (

            {"colunas": colunas_resp, "rows": []},

            _PREVIEW_OCULTO,

            [],

            [],

            alert_children,

            alert_open,

            alert_color,

            meta,

            html.P("Nenhuma linha no período."),

        )



    preview_options = [{"label": c, "value": c} for c in colunas_resp]

    tabela = _montar_datatable(colunas_resp, rows)



    return (

        {"colunas": colunas_resp, "rows": rows},

        {},

        preview_options,

        list(colunas_resp),

        alert_children,

        alert_open,

        alert_color,

        meta,

        tabela,

    )





@callback(

    Output("consultas-db-datatable", "hidden_columns"),

    Input("consultas-db-colunas-preview", "value"),

    State("consultas-db-resultado-store", "data"),

    prevent_initial_call=True,

)

def atualizar_colunas_visiveis(visiveis, store):

    if not store or not store.get("colunas"):

        return no_update

    if not visiveis:

        return no_update

    return _colunas_ocultas(store["colunas"], visiveis)





@callback(

    Output("consultas-db-download", "data"),

    Output("consultas-db-alerta", "children", allow_duplicate=True),

    Output("consultas-db-alerta", "is_open", allow_duplicate=True),

    Output("consultas-db-alerta", "color", allow_duplicate=True),

    Input("consultas-db-btn-csv", "n_clicks"),

    State("consultas-db-tabela", "value"),

    State("consultas-db-colunas", "value"),

    State("consultas-db-datas", "start_date"),

    State("consultas-db-datas", "end_date"),

    State("consultas-db-catalogo-store", "data"),

    prevent_initial_call=True,

)

def baixar_csv(n_clicks, tabela_id, colunas, start_date, end_date, fontes):

    if not n_clicks:

        return no_update, no_update, no_update, no_update



    fonte = _fonte_por_id(fontes or [], tabela_id)

    payload, erro = _build_payload(tabela_id, colunas, start_date, end_date, fonte)

    if erro:

        return no_update, erro, True, "danger"



    ok, resultado = post_bytes("/consultas-db/exportar-csv", payload)

    if not ok:

        return no_update, resultado, True, "danger"



    content, filename = resultado

    download_data = {

        "content": base64.b64encode(content).decode(),

        "filename": filename,

        "type": "text/csv",

    }

    return download_data, no_update, False, no_update


