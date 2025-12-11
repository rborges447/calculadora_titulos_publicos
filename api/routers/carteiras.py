"""
Router para gerenciamento de carteiras de títulos públicos.

As carteiras permitem gerenciar múltiplos vencimentos de um título,
permitindo ajustar parâmetros individuais sem recalcular todos os títulos.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import uuid

from titulospub.core.carteiras import (
    CarteiraLTN,
    CarteiraLFT,
    CarteiraNTNB,
    CarteiraNTNF,
)
from api.models import (
    CarteiraCreateRequest,
    CarteiraUpdateTaxaRequest,
    CarteiraUpdatePremioDIRequest,
    CarteiraUpdateDiasRequest,
    CarteiraUpdateQuantidadeRequest,
    CarteiraResponse,
    TituloCarteiraData,
)

router = APIRouter(prefix="/carteiras", tags=["Carteiras"])

# Armazena carteiras em memória (em produção, usar banco de dados ou cache)
_carteiras: Dict[str, Dict] = {}


def _criar_id_carteira(tipo: str) -> str:
    """Cria um ID único para a carteira"""
    return f"{tipo}_{uuid.uuid4().hex[:8]}"


# ==================== ROTAS DE CRIAÇÃO ====================

@router.post("/ltn", response_model=CarteiraResponse, summary="Criar carteira LTN")
def criar_carteira_ltn(request: CarteiraCreateRequest):
    """
    Cria uma nova carteira LTN com todos os vencimentos disponíveis.
    """
    try:
        carteira = CarteiraLTN(
            data_base=request.data_base,
            dias_liquidacao=request.dias_liquidacao,
            quantidade_padrao=request.quantidade_padrao or 50000,
            tipo_entrada=request.tipo_entrada or "taxa",
        )
        
        carteira_id = _criar_id_carteira("ltn")
        _carteiras[carteira_id] = {
            "tipo": "ltn",
            "carteira": carteira,
        }
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo="LTN",
            data_base=request.data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lft", response_model=CarteiraResponse, summary="Criar carteira LFT")
def criar_carteira_lft(request: CarteiraCreateRequest):
    """
    Cria uma nova carteira LFT com todos os vencimentos disponíveis.
    """
    try:
        carteira = CarteiraLFT(
            data_base=request.data_base,
            dias_liquidacao=request.dias_liquidacao,
            quantidade_padrao=request.quantidade_padrao or 10000,
        )
        
        carteira_id = _criar_id_carteira("lft")
        _carteiras[carteira_id] = {
            "tipo": "lft",
            "carteira": carteira,
        }
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo="LFT",
            data_base=request.data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ntnb", response_model=CarteiraResponse, summary="Criar carteira NTNB")
def criar_carteira_ntnb(request: CarteiraCreateRequest):
    """
    Cria uma nova carteira NTNB com todos os vencimentos disponíveis.
    """
    try:
        carteira = CarteiraNTNB(
            data_base=request.data_base,
            dias_liquidacao=request.dias_liquidacao,
            quantidade_padrao=request.quantidade_padrao or 10000,
        )
        
        carteira_id = _criar_id_carteira("ntnb")
        _carteiras[carteira_id] = {
            "tipo": "ntnb",
            "carteira": carteira,
        }
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo="NTNB",
            data_base=request.data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ntnf", response_model=CarteiraResponse, summary="Criar carteira NTNF")
def criar_carteira_ntnf(request: CarteiraCreateRequest):
    """
    Cria uma nova carteira NTNF com todos os vencimentos disponíveis.
    """
    try:
        carteira = CarteiraNTNF(
            data_base=request.data_base,
            dias_liquidacao=request.dias_liquidacao,
            quantidade_padrao=request.quantidade_padrao or 50000,
            tipo_entrada=request.tipo_entrada or "taxa",
        )
        
        carteira_id = _criar_id_carteira("ntnf")
        _carteiras[carteira_id] = {
            "tipo": "ntnf",
            "carteira": carteira,
        }
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo="NTNF",
            data_base=request.data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTAS DE ATUALIZAÇÃO (ESPECÍFICAS - DEVEM VIR ANTES DA GENÉRICA) ====================

@router.put("/{carteira_id}/taxa", response_model=CarteiraResponse, summary="Atualizar taxa")
def atualizar_taxa_carteira(carteira_id: str, request: CarteiraUpdateTaxaRequest):
    """
    Atualiza a taxa de um título específico na carteira.
    """
    if carteira_id not in _carteiras:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    tipo_carteira = _carteiras[carteira_id]["tipo"]
    if tipo_carteira not in ["ltn", "ntnb", "ntnf"]:
        raise HTTPException(status_code=400, detail=f"Carteira do tipo {tipo_carteira.upper()} não suporta atualização de taxa")
    
    try:
        carteira = _carteiras[carteira_id]["carteira"]
        carteira.atualizar_taxa(request.vencimento, request.taxa)
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo=tipo_carteira.upper(),
            data_base=carteira._data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{carteira_id}/premio-di", response_model=CarteiraResponse, summary="Atualizar prêmio+DI")
def atualizar_premio_di_carteira(carteira_id: str, request: CarteiraUpdatePremioDIRequest):
    """
    Atualiza prêmio e DI de um título específico na carteira.
    """
    if carteira_id not in _carteiras:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    tipo_carteira = _carteiras[carteira_id]["tipo"]
    if tipo_carteira not in ["ltn", "ntnf"]:
        raise HTTPException(status_code=400, detail=f"Carteira do tipo {tipo_carteira.upper()} não suporta prêmio+DI")
    
    try:
        carteira = _carteiras[carteira_id]["carteira"]
        carteira.atualizar_premio_di(request.vencimento, request.premio, request.di)
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo=tipo_carteira.upper(),
            data_base=carteira._data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{carteira_id}/dias", response_model=CarteiraResponse, summary="Atualizar dias de liquidação")
def atualizar_dias_liquidacao_carteira(carteira_id: str, request: CarteiraUpdateDiasRequest):
    """
    Atualiza dias de liquidação para todos os títulos da carteira.
    """
    if carteira_id not in _carteiras:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    try:
        carteira = _carteiras[carteira_id]["carteira"]
        tipo_carteira = _carteiras[carteira_id]["tipo"]
        carteira.atualizar_dias_liquidacao(request.dias)
        
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo=tipo_carteira.upper(),
            data_base=carteira._data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTA GENÉRICA (DEVE VIR POR ÚLTIMO) ====================

@router.get("/{carteira_id}", response_model=CarteiraResponse, summary="Obter dados da carteira")
def obter_carteira(carteira_id: str):
    """
    Obtém os dados atuais da carteira.
    """
    if carteira_id not in _carteiras:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    
    try:
        carteira = _carteiras[carteira_id]["carteira"]
        tipo_carteira = _carteiras[carteira_id]["tipo"]
        dados_tabela = carteira.obter_dados_tabela()
        titulos = [TituloCarteiraData(**dado) for dado in dados_tabela]
        
        return CarteiraResponse(
            carteira_id=carteira_id,
            tipo=tipo_carteira.upper(),
            data_base=carteira._data_base,
            dias_liquidacao=carteira._dias_liquidacao,
            total_titulos=carteira.total_titulos,
            titulos=titulos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

