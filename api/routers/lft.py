"""
Endpoints para título LFT (Letra Financeira do Tesouro)
"""
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, HTTPException

from api.models import LFTRequest, LFTResponse
from titulospub import LFT

router = APIRouter(prefix="/titulos/lft", tags=["LFT"])


def _serialize_datetime(dt) -> str:
    """Serializa datetime para string ISO"""
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        return dt.strftime("%Y-%m-%d")
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return str(dt)


@router.post("", response_model=LFTResponse, summary="Criar título LFT")
def criar_lft(request: LFTRequest):
    """
    Cria e calcula um título LFT (Letra Financeira do Tesouro)
    
    - **data_vencimento**: Data de vencimento do título (YYYY-MM-DD)
    - **taxa**: Taxa de juros (opcional, usa ANBIMA se não informado)
    - **quantidade**: Quantidade de títulos (opcional)
    - **financeiro**: Valor financeiro em R$ (opcional, alternativo à quantidade)
    """
    try:
        # Criar instância do título
        kwargs = {
            "data_vencimento_titulo": request.data_vencimento,
            "dias_liquidacao": request.dias_liquidacao or 1,
        }
        
        if request.data_base:
            kwargs["data_base"] = request.data_base
        if request.taxa is not None:
            kwargs["taxa"] = request.taxa
        if request.quantidade is not None:
            kwargs["quantidade"] = request.quantidade
        
        titulo = LFT(**kwargs)
        
        # Definir quantidade ou financeiro
        if request.financeiro is not None:
            titulo.financeiro = request.financeiro
        elif request.quantidade is not None:
            titulo.quantidade = request.quantidade
        
        # Construir resposta
        return LFTResponse(
            tipo="LFT",
            nome=getattr(titulo, "_nome", "LFT"),
            data_vencimento=_serialize_datetime(titulo._data_vencimento_titulo),
            data_base=_serialize_datetime(titulo.data_base),
            data_liquidacao=_serialize_datetime(titulo.data_liquidacao),
            dias_liquidacao=titulo.dias_liquidacao,
            taxa=titulo.taxa,
            quantidade=titulo.quantidade,
            financeiro=titulo.financeiro,
            pu_d0=titulo.pu_d0,
            pu_termo=getattr(titulo, "pu_termo", None),
            pu_carregado=getattr(titulo, "pu_carregado", None),
            cotacao=getattr(titulo, "cotacap", None),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






