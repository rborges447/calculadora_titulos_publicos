"""
Endpoints para título NTNB (Nota do Tesouro Nacional - Série B)
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import pandas as pd

from titulospub import NTNB
from api.models import NTNBRequest, NTNBResponse, NTNBHedgeDIRequest, NTNBHedgeDIResponse

router = APIRouter(prefix="/titulos/ntnb", tags=["NTNB"])


def _serialize_datetime(dt) -> str:
    """Serializa datetime para string ISO"""
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        return dt.strftime("%Y-%m-%d")
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return str(dt)


@router.post("", response_model=NTNBResponse, summary="Criar título NTNB")
def criar_ntnb(request: NTNBRequest):
    """
    Cria e calcula um título NTNB (Nota do Tesouro Nacional - Série B)
    
    - **data_vencimento**: Data de vencimento do título (YYYY-MM-DD)
    - **taxa**: Taxa de juros (opcional, usa ANBIMA se não informado)
    - **premio**: Prêmio sobre DAP (opcional)
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
        
        # Se tem prêmio + taxa_dap, calcular a taxa: taxa = taxa_dap + premio/100
        if request.premio is not None and request.taxa_dap is not None:
            # Calcular taxa a partir de taxa_dap + prêmio
            taxa_calculada = float(request.taxa_dap) + float(request.premio) / 100
            kwargs["taxa"] = taxa_calculada
        elif request.taxa is not None:
            kwargs["taxa"] = request.taxa
        elif request.premio is not None:
            # Se só tem prêmio (sem taxa_dap), usar o comportamento padrão da classe
            kwargs["premio"] = request.premio
        
        if request.quantidade is not None:
            kwargs["quantidade"] = request.quantidade
        
        titulo = NTNB(**kwargs)
        
        # Definir quantidade ou financeiro
        if request.financeiro is not None:
            titulo.financeiro = request.financeiro
        elif request.quantidade is not None:
            titulo.quantidade = request.quantidade
        
        # Construir resposta
        return NTNBResponse(
            tipo="NTNB",
            nome=getattr(titulo, "_nome", "NTNB"),
            data_vencimento=_serialize_datetime(titulo._data_vencimento_titulo),
            data_base=_serialize_datetime(titulo.data_base),
            data_liquidacao=_serialize_datetime(titulo.data_liquidacao),
            dias_liquidacao=titulo.dias_liquidacao,
            taxa=titulo.taxa,
            quantidade=titulo.quantidade,
            financeiro=titulo.financeiro,
            pu_d0=titulo.pu_d0,
            pu_termo=titulo.pu_termo,
            pu_carregado=getattr(titulo, "pu_carregado", None),
            pu_ajustado=getattr(titulo, "pu_ajustado", None),
            dv01=getattr(titulo, "dv01", None),
            carrego_brl=getattr(titulo, "carrego_brl", None),
            carrego_bps=getattr(titulo, "carrego_bps", None),
            premio=getattr(titulo, "premio", None),
            cotacao=getattr(titulo, "cotacao", None),
            duration=getattr(titulo, "duration", None),
            data_vencimento_duration=_serialize_datetime(getattr(titulo, "_data_vencimento_duration", None)),
            dias_duration=getattr(titulo, "_dias_duration", None),
            ajuste_dap=getattr(titulo, "ajuste_dap", None),
            premio_anbima_dap=getattr(titulo, "premio_anbima_dap", None),
            hedge_dap=getattr(titulo, "hedge_dap", None),
            vna=getattr(titulo, "_vna", None),
            vna_tesouro=getattr(titulo, "_vna_tesouro", None),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/hedge-di", response_model=NTNBHedgeDIResponse, summary="Calcular hedge DI para NTNB")
def calcular_hedge_di_ntnb(request: NTNBHedgeDIRequest):
    """
    Calcula o hedge DI para um título NTNB usando um código DI específico
    
    - **data_vencimento**: Data de vencimento do título NTNB (YYYY-MM-DD)
    - **codigo_di**: Código do contrato DI (ex: "DI1F32")
    - **quantidade**: Quantidade de títulos (opcional)
    - **financeiro**: Valor financeiro em R$ (opcional, alternativo à quantidade)
    - **taxa**: Taxa de juros (opcional, usa ANBIMA se não informado)
    """
    try:
        # Criar instância do título NTNB
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
        if request.quantidade is not None:
            kwargs["quantidade"] = request.quantidade
        
        titulo = NTNB(**kwargs)
        
        # Definir quantidade ou financeiro
        if request.financeiro is not None:
            titulo.financeiro = request.financeiro
        elif request.quantidade is not None:
            titulo.quantidade = request.quantidade
        
        # Calcular hedge DI usando o método da classe
        hedge_di = titulo.calcular_hedge_di(codigo_di=request.codigo_di)
        
        # Buscar ajuste DI usado
        curva_di = titulo._vm.get_bmf()["DI"]
        serie_adj = curva_di.loc[curva_di["DI"] == request.codigo_di, "ADJ"]
        ajuste_di = float(serie_adj.iloc[0]) if not serie_adj.empty else None
        
        # Construir resposta
        return NTNBHedgeDIResponse(
            tipo="NTNB",
            data_vencimento=_serialize_datetime(titulo._data_vencimento_titulo),
            codigo_di=request.codigo_di,
            quantidade=titulo.quantidade,
            financeiro=titulo.financeiro,
            dv01_ntnb=titulo.dv01,
            hedge_di=hedge_di,
            ajuste_di=ajuste_di,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

