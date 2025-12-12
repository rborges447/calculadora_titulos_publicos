"""
Endpoints para título NTNF (Nota do Tesouro Nacional - Série F)
"""
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, HTTPException

from api.models import NTNFRequest, NTNFResponse
from titulospub import NTNF

router = APIRouter(prefix="/titulos/ntnf", tags=["NTNF"])


def _serialize_datetime(dt) -> str:
    """Serializa datetime para string ISO"""
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        return dt.strftime("%Y-%m-%d")
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return str(dt)


@router.post("", response_model=NTNFResponse, summary="Criar título NTNF")
def criar_ntnf(request: NTNFRequest):
    """
    Cria e calcula um título NTNF (Nota do Tesouro Nacional - Série F)
    
    - **data_vencimento**: Data de vencimento do título (YYYY-MM-DD)
    - **taxa**: Taxa de juros (opcional, usa ANBIMA se não informado)
    - **premio**: Prêmio sobre DI (opcional)
    - **di**: Taxa DI de referência (opcional)
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
        if request.premio is not None:
            kwargs["premio"] = request.premio
        if request.di is not None:
            kwargs["di"] = request.di
        if request.quantidade is not None:
            kwargs["quantidade"] = request.quantidade
        
        titulo = NTNF(**kwargs)
        
        # Definir quantidade ou financeiro
        if request.financeiro is not None:
            titulo.financeiro = request.financeiro
        elif request.quantidade is not None:
            titulo.quantidade = request.quantidade
        
        # Construir resposta
        return NTNFResponse(
            tipo="NTNF",
            nome=getattr(titulo, "_nome", "NTNF"),
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
            dv01=getattr(titulo, "dv01", None),
            carrego_brl=getattr(titulo, "carrego_brl", None),
            carrego_bps=getattr(titulo, "carrego_bps", None),
            premio=getattr(titulo, "premio", None),
            di=getattr(titulo, "di", None),
            ajuste_di=getattr(titulo, "ajuste_di", None),
            premio_anbima=getattr(titulo, "premio_anbima", None),
            hedge_di=getattr(titulo, "hedge_di", None),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






