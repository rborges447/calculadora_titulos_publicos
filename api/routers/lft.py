"""
Endpoints para título LFT (Letra Financeira do Tesouro)
"""
from fastapi import APIRouter, HTTPException

from api.logging_config import get_logger
from api.models import LFTRequest, LFTResponse
from api.utils import serialize_datetime
from titulospub import LFT

router = APIRouter(prefix="/titulos/lft", tags=["LFT"])
logger = get_logger("api.routers.lft")


@router.post("", response_model=LFTResponse, summary="Criar título LFT")
def criar_lft(request: LFTRequest) -> LFTResponse:
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
            "dias_liquidacao": request.dias_liquidacao if request.dias_liquidacao is not None else 1,
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
            data_vencimento=serialize_datetime(titulo._data_vencimento_titulo),
            data_base=serialize_datetime(titulo.data_base),
            data_liquidacao=serialize_datetime(titulo.data_liquidacao),
            dias_liquidacao=titulo.dias_liquidacao,
            taxa=titulo.taxa,
            quantidade=titulo.quantidade,
            financeiro=titulo.financeiro,
            pu_d0=titulo.pu_d0,
            pu_termo=titulo.pu_termo,  # pu_termo sempre está disponível após cálculo
            pu_carregado=titulo.pu_carregado if titulo.pu_carregado is not None else None,
            cotacao=titulo.cotacap if hasattr(titulo, 'cotacap') and titulo.cotacap is not None else None,
            taxa_anbima=titulo.taxa_anbima if hasattr(titulo, 'taxa_anbima') else None,
        )
    except ValueError as e:
        logger.warning(f"Erro de validação ao criar LFT: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Erro interno ao criar LFT: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao criar título LFT: {str(e)}"
        )






