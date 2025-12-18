"""
Router para gerenciamento de carteiras de títulos públicos.

As carteiras permitem gerenciar múltiplos vencimentos de um título,
permitindo ajustar parâmetros individuais sem recalcular todos os títulos.

NOTA: Esta implementação usa estado em memória que não funciona com múltiplos workers.
Para produção com múltiplos workers, considere usar banco de dados ou cache compartilhado (Redis).
"""
import threading
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException

from api.models import (
    CarteiraCreateRequest,
    CarteiraResponse,
    CarteiraUpdateDiasRequest,
    CarteiraUpdatePremioDIRequest,
    CarteiraUpdateQuantidadeRequest,
    CarteiraUpdateTaxaRequest,
    TituloCarteiraData,
)
from titulospub.core.carteiras import (
    CarteiraLFT,
    CarteiraLTN,
    CarteiraNTNB,
    CarteiraNTNF,
)

router = APIRouter(prefix="/carteiras", tags=["Carteiras"])

# Armazena carteiras em memória com lock para thread-safety
# LIMITAÇÃO: Não funciona com múltiplos workers (cada worker tem sua própria memória)
# SOLUÇÃO FUTURA: Migrar para banco de dados ou cache compartilhado (Redis)
_carteiras: Dict[str, Dict] = {}
_carteiras_lock = threading.Lock()


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
        with _carteiras_lock:
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
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar carteira. Verifique os logs do servidor."
        )


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
        with _carteiras_lock:
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
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar carteira. Verifique os logs do servidor."
        )


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
        with _carteiras_lock:
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
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar carteira. Verifique os logs do servidor."
        )


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
        with _carteiras_lock:
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
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar carteira. Verifique os logs do servidor."
        )


# ==================== ROTAS DE ATUALIZAÇÃO (ESPECÍFICAS - DEVEM VIR ANTES DA GENÉRICA) ====================

@router.put("/{carteira_id}/taxa", response_model=CarteiraResponse, summary="Atualizar taxa")
def atualizar_taxa_carteira(carteira_id: str, request: CarteiraUpdateTaxaRequest):
    """
    Atualiza a taxa de um título específico na carteira.
    """
    with _carteiras_lock:
        if carteira_id not in _carteiras:
            raise HTTPException(status_code=404, detail="Carteira não encontrada")
        
        tipo_carteira = _carteiras[carteira_id]["tipo"]
        if tipo_carteira not in ["ltn", "lft", "ntnb", "ntnf"]:
            raise HTTPException(status_code=400, detail=f"Carteira do tipo {tipo_carteira.upper()} não suporta atualização de taxa")
        
        carteira = _carteiras[carteira_id]["carteira"]
    
    try:
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
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao atualizar carteira. Verifique os logs do servidor."
        )


@router.put("/{carteira_id}/premio-di", response_model=CarteiraResponse, summary="Atualizar prêmio+DI")
def atualizar_premio_di_carteira(carteira_id: str, request: CarteiraUpdatePremioDIRequest):
    """
    Atualiza prêmio e DI de um título específico na carteira.
    """
    with _carteiras_lock:
        if carteira_id not in _carteiras:
            raise HTTPException(status_code=404, detail="Carteira não encontrada")
        
        tipo_carteira = _carteiras[carteira_id]["tipo"]
        if tipo_carteira not in ["ltn", "ntnf"]:
            raise HTTPException(status_code=400, detail=f"Carteira do tipo {tipo_carteira.upper()} não suporta prêmio+DI")
        
        carteira = _carteiras[carteira_id]["carteira"]
    
    try:
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
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao atualizar carteira. Verifique os logs do servidor."
        )


@router.put("/{carteira_id}/dias", response_model=CarteiraResponse, summary="Atualizar dias de liquidação")
def atualizar_dias_liquidacao_carteira(carteira_id: str, request: CarteiraUpdateDiasRequest):
    """
    Atualiza dias de liquidação para todos os títulos da carteira.
    """
    with _carteiras_lock:
        if carteira_id not in _carteiras:
            raise HTTPException(status_code=404, detail="Carteira não encontrada")
        
        carteira = _carteiras[carteira_id]["carteira"]
        tipo_carteira = _carteiras[carteira_id]["tipo"]
    
    try:
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
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar carteira. Verifique os logs do servidor."
        )


# ==================== ROTA GENÉRICA (DEVE VIR POR ÚLTIMO) ====================

@router.get("/{carteira_id}", response_model=CarteiraResponse, summary="Obter dados da carteira")
def obter_carteira(carteira_id: str):
    """
    Obtém os dados atuais da carteira.
    """
    with _carteiras_lock:
        if carteira_id not in _carteiras:
            raise HTTPException(status_code=404, detail="Carteira não encontrada")
        
        carteira = _carteiras[carteira_id]["carteira"]
        tipo_carteira = _carteiras[carteira_id]["tipo"]
    
    try:
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
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar carteira. Verifique os logs do servidor."
        )

