"""
Endpoints para título LTN (Letra do Tesouro Nacional)
"""
from fastapi import APIRouter, HTTPException

from api.models import LTNRequest, LTNResponse
from api.utils import serialize_datetime
from titulospub import LTN

router = APIRouter(prefix="/titulos/ltn", tags=["LTN"])


@router.post("", response_model=LTNResponse, summary="Criar título LTN")
def criar_ltn(request: LTNRequest):
    """
    Cria e calcula um título LTN (Letra do Tesouro Nacional)
    
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
            "dias_liquidacao": request.dias_liquidacao if request.dias_liquidacao is not None else 1,
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
        
        titulo = LTN(**kwargs)
        
        # Definir quantidade ou financeiro
        if request.financeiro is not None:
            titulo.financeiro = request.financeiro
        elif request.quantidade is not None:
            titulo.quantidade = request.quantidade
        
        # Construir resposta
        return LTNResponse(
            tipo="LTN",
            nome=getattr(titulo, "_nome", "LTN"),
            data_vencimento=serialize_datetime(titulo._data_vencimento_titulo),
            data_base=serialize_datetime(titulo.data_base),
            data_liquidacao=serialize_datetime(titulo.data_liquidacao),
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
            taxa_anbima=getattr(titulo, "taxa_anbima", None),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao criar título LTN: {str(e)}"
        )






