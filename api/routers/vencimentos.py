"""
Endpoints para obter listas de vencimentos e códigos disponíveis
"""
from fastapi import APIRouter
from typing import List, Dict

from titulospub.dados.vencimentos import (
    get_vencimentos_ltn,
    get_vencimentos_lft,
    get_vencimentos_ntnb,
    get_vencimentos_ntnf,
    get_codigos_di_disponiveis,
    get_todos_vencimentos,
)

router = APIRouter(prefix="/vencimentos", tags=["Vencimentos"])


@router.get("/ltn", response_model=List[str], summary="Vencimentos LTN")
def vencimentos_ltn():
    """
    Retorna lista de vencimentos disponíveis para LTN.
    """
    return get_vencimentos_ltn()


@router.get("/lft", response_model=List[str], summary="Vencimentos LFT")
def vencimentos_lft():
    """
    Retorna lista de vencimentos disponíveis para LFT.
    """
    return get_vencimentos_lft()


@router.get("/ntnb", response_model=List[str], summary="Vencimentos NTNB")
def vencimentos_ntnb():
    """
    Retorna lista de vencimentos disponíveis para NTNB.
    """
    return get_vencimentos_ntnb()


@router.get("/ntnf", response_model=List[str], summary="Vencimentos NTNF")
def vencimentos_ntnf():
    """
    Retorna lista de vencimentos disponíveis para NTNF.
    """
    return get_vencimentos_ntnf()


@router.get("/di", response_model=List[str], summary="Códigos DI disponíveis")
def codigos_di():
    """
    Retorna lista de códigos DI disponíveis.
    """
    return get_codigos_di_disponiveis()


@router.get("/todos", response_model=Dict[str, List[str]], summary="Todos os vencimentos")
def todos_vencimentos():
    """
    Retorna todos os vencimentos disponíveis por título.
    """
    return get_todos_vencimentos()

