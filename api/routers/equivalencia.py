"""
Endpoints para cálculo de equivalência entre títulos públicos
"""
from fastapi import APIRouter, HTTPException

from titulospub import equivalencia
from api.models import EquivalenciaRequest, EquivalenciaResponse

router = APIRouter(prefix="/equivalencia", tags=["Equivalência"])


@router.post("", response_model=EquivalenciaResponse, summary="Calcular equivalência entre títulos")
def calcular_equivalencia(request: EquivalenciaRequest):
    """
    Calcula a equivalência entre dois títulos públicos
    
    - **titulo1**: Tipo do primeiro título (NTNB, LTN, LFT, NTNF)
    - **venc1**: Data de vencimento do primeiro título (YYYY-MM-DD)
    - **titulo2**: Tipo do segundo título (NTNB, LTN, LFT, NTNF)
    - **venc2**: Data de vencimento do segundo título (YYYY-MM-DD)
    - **qtd1**: Quantidade do primeiro título
    - **tx1**: Taxa do primeiro título (opcional, usa ANBIMA se não informado)
    - **tx2**: Taxa do segundo título (opcional, usa ANBIMA se não informado)
    - **criterio**: Critério de equivalência - "dv" (DV01) ou "fin" (financeiro)
    
    Retorna a quantidade equivalente do segundo título baseada no critério escolhido.
    """
    try:
        # Validar critério
        if request.criterio not in ["dv", "fin"]:
            raise ValueError(f"Critério '{request.criterio}' inválido. Use 'dv' ou 'fin'")
        
        # Preparar parâmetros
        kwargs = {
            "titulo1": request.titulo1,
            "venc1": request.venc1,
            "titulo2": request.titulo2,
            "venc2": request.venc2,
            "qtd1": request.qtd1,
            "criterio": request.criterio
        }
        
        # Adicionar taxas se fornecidas
        if request.tx1 is not None:
            kwargs["tx1"] = request.tx1
        if request.tx2 is not None:
            kwargs["tx2"] = request.tx2
        
        # Calcular equivalência
        equivalencia_calculada = equivalencia(**kwargs)
        
        # Construir resposta
        return EquivalenciaResponse(
            titulo1=request.titulo1,
            venc1=request.venc1,
            titulo2=request.titulo2,
            venc2=request.venc2,
            qtd1=request.qtd1,
            equivalencia=equivalencia_calculada,
            criterio=request.criterio
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular equivalência: {str(e)}")



