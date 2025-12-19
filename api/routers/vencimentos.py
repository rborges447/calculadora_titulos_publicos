"""
Endpoints para obter listas de vencimentos e códigos disponíveis
"""

from typing import Dict, List

from fastapi import APIRouter

from api.models import CodigosDIResponse, TodosVencimentosResponse, VencimentosResponse
from titulospub.dados.vencimentos import (
    get_codigos_di_disponiveis,
    get_todos_vencimentos,
    get_vencimentos_lft,
    get_vencimentos_ltn,
    get_vencimentos_ntnb,
    get_vencimentos_ntnf,
)

router = APIRouter(prefix="/vencimentos", tags=["Vencimentos"])


@router.get("/ltn", response_model=List[str], summary="Vencimentos LTN")
def vencimentos_ltn():
    """
    Retorna lista de vencimentos disponíveis para LTN.

    Retorna uma lista simples de strings no formato YYYY-MM-DD.
    Para resposta estruturada com metadados, use /vencimentos/ltn/detalhes
    """
    return get_vencimentos_ltn()


@router.get(
    "/ltn/detalhes", response_model=VencimentosResponse, summary="Vencimentos LTN (detalhado)"
)
def vencimentos_ltn_detalhes():
    """
    Retorna lista de vencimentos disponíveis para LTN com metadados.
    """
    vencimentos = get_vencimentos_ltn()
    return VencimentosResponse(vencimentos=vencimentos, total=len(vencimentos))


@router.get("/lft", response_model=List[str], summary="Vencimentos LFT")
def vencimentos_lft():
    """
    Retorna lista de vencimentos disponíveis para LFT.

    Retorna uma lista simples de strings no formato YYYY-MM-DD.
    """
    return get_vencimentos_lft()


@router.get(
    "/lft/detalhes", response_model=VencimentosResponse, summary="Vencimentos LFT (detalhado)"
)
def vencimentos_lft_detalhes():
    """
    Retorna lista de vencimentos disponíveis para LFT com metadados.
    """
    vencimentos = get_vencimentos_lft()
    return VencimentosResponse(vencimentos=vencimentos, total=len(vencimentos))


@router.get("/ntnb", response_model=List[str], summary="Vencimentos NTNB")
def vencimentos_ntnb():
    """
    Retorna lista de vencimentos disponíveis para NTNB.

    Retorna uma lista simples de strings no formato YYYY-MM-DD.
    """
    return get_vencimentos_ntnb()


@router.get(
    "/ntnb/detalhes", response_model=VencimentosResponse, summary="Vencimentos NTNB (detalhado)"
)
def vencimentos_ntnb_detalhes():
    """
    Retorna lista de vencimentos disponíveis para NTNB com metadados.
    """
    vencimentos = get_vencimentos_ntnb()
    return VencimentosResponse(vencimentos=vencimentos, total=len(vencimentos))


@router.get("/ntnf", response_model=List[str], summary="Vencimentos NTNF")
def vencimentos_ntnf():
    """
    Retorna lista de vencimentos disponíveis para NTNF.

    Retorna uma lista simples de strings no formato YYYY-MM-DD.
    """
    return get_vencimentos_ntnf()


@router.get(
    "/ntnf/detalhes", response_model=VencimentosResponse, summary="Vencimentos NTNF (detalhado)"
)
def vencimentos_ntnf_detalhes():
    """
    Retorna lista de vencimentos disponíveis para NTNF com metadados.
    """
    vencimentos = get_vencimentos_ntnf()
    return VencimentosResponse(vencimentos=vencimentos, total=len(vencimentos))


@router.get("/di", response_model=List[str], summary="Códigos DI disponíveis")
def codigos_di():
    """
    Retorna lista de códigos DI disponíveis.

    Retorna uma lista simples de strings com os códigos DI.
    """
    return get_codigos_di_disponiveis()


@router.get("/di/detalhes", response_model=CodigosDIResponse, summary="Códigos DI (detalhado)")
def codigos_di_detalhes():
    """
    Retorna lista de códigos DI disponíveis com metadados.
    """
    codigos = get_codigos_di_disponiveis()
    return CodigosDIResponse(codigos=codigos, total=len(codigos))


@router.get("/todos", response_model=Dict[str, List[str]], summary="Todos os vencimentos")
def todos_vencimentos():
    """
    Retorna todos os vencimentos disponíveis por título.

    Retorna um dicionário com listas simples de strings.
    """
    return get_todos_vencimentos()


@router.get(
    "/todos/detalhes",
    response_model=TodosVencimentosResponse,
    summary="Todos os vencimentos (detalhado)",
)
def todos_vencimentos_detalhes():
    """
    Retorna todos os vencimentos disponíveis por título com estrutura validada.
    """
    todos = get_todos_vencimentos()
    return TodosVencimentosResponse(
        ltn=todos.get("ltn", []),
        lft=todos.get("lft", []),
        ntnb=todos.get("ntnb", []),
        ntnf=todos.get("ntnf", []),
    )
