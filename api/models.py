"""
Modelos Pydantic para validação de requests e responses da API

Os modelos Pydantic servem para:
1. Validar automaticamente os dados de entrada (requests)
2. Definir a estrutura dos dados de saída (responses)
3. Gerar documentação automática na API
4. Fornecer type hints para melhor desenvolvimento
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== REQUEST MODELS ====================
# Cada título tem sua própria classe completa, sem herança

class LTNRequest(BaseModel):
    """Request model para criação de título LTN (Letra do Tesouro Nacional)"""
    data_vencimento: str = Field(
        ..., 
        description="Data de vencimento do título (formato: YYYY-MM-DD)",
        example="2025-01-01"
    )
    data_base: Optional[str] = Field(
        None, 
        description="Data base para cálculos (formato: YYYY-MM-DD). Se não informado, usa a data atual",
        example="2024-12-01"
    )
    dias_liquidacao: Optional[int] = Field(
        1, 
        description="Dias para liquidação (padrão: 1)",
        ge=0,
        example=1
    )
    taxa: Optional[float] = Field(
        None, 
        description="Taxa de juros do título (%). Se não informado, usa taxa ANBIMA",
        example=12.5
    )
    premio: Optional[float] = Field(
        None, 
        description="Prêmio sobre DI em pontos base (ex: 0.5 = 50 bps)",
        example=0.5
    )
    di: Optional[float] = Field(
        None, 
        description="Taxa DI de referência (%). Usado junto com premio para calcular taxa",
        example=13.0
    )
    quantidade: Optional[float] = Field(
        None, 
        description="Quantidade de títulos. Use este OU financeiro (não ambos)",
        gt=0,
        example=50000
    )
    financeiro: Optional[float] = Field(
        None, 
        description="Valor financeiro da posição em R$. Use este OU quantidade (não ambos)",
        gt=0,
        example=100000
    )


class LFTRequest(BaseModel):
    """Request model para criação de título LFT (Letra Financeira do Tesouro)"""
    data_vencimento: str = Field(
        ..., 
        description="Data de vencimento do título (formato: YYYY-MM-DD)",
        example="2025-01-01"
    )
    data_base: Optional[str] = Field(
        None, 
        description="Data base para cálculos (formato: YYYY-MM-DD). Se não informado, usa a data atual",
        example="2024-12-01"
    )
    dias_liquidacao: Optional[int] = Field(
        1, 
        description="Dias para liquidação (padrão: 1)",
        ge=0,
        example=1
    )
    taxa: Optional[float] = Field(
        None, 
        description="Taxa de juros do título (%). Se não informado, usa taxa ANBIMA",
        example=12.5
    )
    quantidade: Optional[float] = Field(
        None, 
        description="Quantidade de títulos. Use este OU financeiro (não ambos)",
        gt=0,
        example=10000
    )
    financeiro: Optional[float] = Field(
        None, 
        description="Valor financeiro da posição em R$. Use este OU quantidade (não ambos)",
        gt=0,
        example=100000
    )


class NTNBRequest(BaseModel):
    """Request model para criação de título NTNB (Nota do Tesouro Nacional - Série B)"""
    data_vencimento: str = Field(
        ..., 
        description="Data de vencimento do título (formato: YYYY-MM-DD)",
        example="2035-05-15"
    )
    data_base: Optional[str] = Field(
        None, 
        description="Data base para cálculos (formato: YYYY-MM-DD). Se não informado, usa a data atual",
        example="2024-12-01"
    )
    dias_liquidacao: Optional[int] = Field(
        1, 
        description="Dias para liquidação (padrão: 1)",
        ge=0,
        example=1
    )
    taxa: Optional[float] = Field(
        None, 
        description="Taxa de juros do título (%). Se não informado, usa taxa ANBIMA",
        example=7.53
    )
    premio: Optional[float] = Field(
        None, 
        description="Prêmio sobre DAP em pontos base (ex: 0.5 = 50 bps)",
        example=0.5
    )
    taxa_dap: Optional[float] = Field(
        None, 
        description="Taxa DAP de referência (%). Usado junto com premio para calcular taxa",
        example=7.0
    )
    quantidade: Optional[float] = Field(
        None, 
        description="Quantidade de títulos. Use este OU financeiro (não ambos)",
        gt=0,
        example=10000
    )
    financeiro: Optional[float] = Field(
        None, 
        description="Valor financeiro da posição em R$. Use este OU quantidade (não ambos)",
        gt=0,
        example=100000
    )


class NTNFRequest(BaseModel):
    """Request model para criação de título NTNF (Nota do Tesouro Nacional - Série F)"""
    data_vencimento: str = Field(
        ..., 
        description="Data de vencimento do título (formato: YYYY-MM-DD)",
        example="2025-01-01"
    )
    data_base: Optional[str] = Field(
        None, 
        description="Data base para cálculos (formato: YYYY-MM-DD). Se não informado, usa a data atual",
        example="2024-12-01"
    )
    dias_liquidacao: Optional[int] = Field(
        1, 
        description="Dias para liquidação (padrão: 1)",
        ge=0,
        example=1
    )
    taxa: Optional[float] = Field(
        None, 
        description="Taxa de juros do título (%). Se não informado, usa taxa ANBIMA",
        example=12.5
    )
    premio: Optional[float] = Field(
        None, 
        description="Prêmio sobre DI em pontos base (ex: 0.3 = 30 bps)",
        example=0.3
    )
    di: Optional[float] = Field(
        None, 
        description="Taxa DI de referência (%). Usado junto com premio para calcular taxa",
        example=13.0
    )
    quantidade: Optional[float] = Field(
        None, 
        description="Quantidade de títulos. Use este OU financeiro (não ambos)",
        gt=0,
        example=50000
    )
    financeiro: Optional[float] = Field(
        None, 
        description="Valor financeiro da posição em R$. Use este OU quantidade (não ambos)",
        gt=0,
        example=100000
    )


class NTNBHedgeDIRequest(BaseModel):
    """Request model para cálculo de hedge DI de um título NTNB"""
    data_vencimento: str = Field(
        ..., 
        description="Data de vencimento do título NTNB (formato: YYYY-MM-DD)",
        example="2035-05-15"
    )
    codigo_di: str = Field(
        ..., 
        description="Código do contrato DI (ex: DI1F32)",
        example="DI1F32"
    )
    data_base: Optional[str] = Field(
        None, 
        description="Data base para cálculos (formato: YYYY-MM-DD). Se não informado, usa a data atual",
        example="2024-12-01"
    )
    dias_liquidacao: Optional[int] = Field(
        1, 
        description="Dias para liquidação (padrão: 1)",
        ge=0,
        example=1
    )
    taxa: Optional[float] = Field(
        None, 
        description="Taxa de juros do título (%). Se não informado, usa taxa ANBIMA",
        example=7.53
    )
    premio: Optional[float] = Field(
        None, 
        description="Prêmio sobre DAP em pontos base (ex: 0.5 = 50 bps)",
        example=0.5
    )
    quantidade: Optional[float] = Field(
        None, 
        description="Quantidade de títulos. Use este OU financeiro (não ambos)",
        gt=0,
        example=10000
    )
    financeiro: Optional[float] = Field(
        None, 
        description="Valor financeiro da posição em R$. Use este OU quantidade (não ambos)",
        gt=0,
        example=100000
    )


class EquivalenciaRequest(BaseModel):
    """Request model para cálculo de equivalência entre títulos"""
    titulo1: str = Field(
        ..., 
        description="Tipo do primeiro título",
        example="LTN"
    )
    venc1: str = Field(
        ..., 
        description="Data de vencimento do primeiro título (formato: YYYY-MM-DD)",
        example="2025-01-01"
    )
    titulo2: str = Field(
        ..., 
        description="Tipo do segundo título",
        example="NTNB"
    )
    venc2: str = Field(
        ..., 
        description="Data de vencimento do segundo título (formato: YYYY-MM-DD)",
        example="2035-05-15"
    )
    qtd1: float = Field(
        ..., 
        description="Quantidade do primeiro título",
        gt=0,
        example=10000
    )
    tx1: Optional[float] = Field(
        None, 
        description="Taxa do primeiro título (%). Se não informado, usa ANBIMA",
        example=12.5
    )
    tx2: Optional[float] = Field(
        None, 
        description="Taxa do segundo título (%). Se não informado, usa ANBIMA",
        example=7.53
    )
    criterio: str = Field(
        ..., 
        description="Critério de equivalência: 'dv' (DV01) ou 'fin' (financeiro)",
        example="dv"
    )


# ==================== RESPONSE MODELS ====================
# Cada título tem sua própria classe de resposta completa, sem herança

class LTNResponse(BaseModel):
    """Response model para título LTN (Letra do Tesouro Nacional)"""
    tipo: str = Field(default="LTN", description="Tipo do título")
    nome: str = Field(..., description="Nome do título")
    data_vencimento: str = Field(..., description="Data de vencimento")
    data_base: str = Field(..., description="Data base")
    data_liquidacao: str = Field(..., description="Data de liquidação")
    dias_liquidacao: int = Field(..., description="Dias para liquidação")
    taxa: float = Field(..., description="Taxa de juros (%)")
    quantidade: float = Field(..., description="Quantidade de títulos")
    financeiro: float = Field(..., description="Valor financeiro (R$)")
    pu_d0: float = Field(..., description="Preço unitário à vista")
    pu_termo: Optional[float] = Field(None, description="Preço unitário a termo")
    pu_carregado: Optional[float] = Field(None, description="Preço unitário carregado")
    dv01: Optional[float] = Field(None, description="DV01 (sensibilidade à mudança de 1bp)")
    carrego_brl: Optional[float] = Field(None, description="Carregamento em BRL")
    carrego_bps: Optional[float] = Field(None, description="Carregamento em pontos base")
    premio: Optional[float] = Field(None, description="Prêmio sobre DI")
    di: Optional[float] = Field(None, description="Taxa DI de referência")
    ajuste_di: Optional[float] = Field(None, description="Ajuste DI")
    premio_anbima: Optional[float] = Field(None, description="Prêmio ANBIMA")
    hedge_di: Optional[int] = Field(None, description="Hedge DI (quantidade de contratos)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class LFTResponse(BaseModel):
    """Response model para título LFT (Letra Financeira do Tesouro)"""
    tipo: str = Field(default="LFT", description="Tipo do título")
    nome: str = Field(..., description="Nome do título")
    data_vencimento: str = Field(..., description="Data de vencimento")
    data_base: str = Field(..., description="Data base")
    data_liquidacao: str = Field(..., description="Data de liquidação")
    dias_liquidacao: int = Field(..., description="Dias para liquidação")
    taxa: float = Field(..., description="Taxa de juros (%)")
    quantidade: float = Field(..., description="Quantidade de títulos")
    financeiro: float = Field(..., description="Valor financeiro (R$)")
    pu_d0: float = Field(..., description="Preço unitário à vista")
    pu_termo: Optional[float] = Field(None, description="Preço unitário a termo")
    pu_carregado: Optional[float] = Field(None, description="Preço unitário carregado")
    cotacao: Optional[float] = Field(None, description="Cotação")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NTNBResponse(BaseModel):
    """Response model para título NTNB (Nota do Tesouro Nacional - Série B)"""
    tipo: str = Field(default="NTNB", description="Tipo do título")
    nome: str = Field(..., description="Nome do título")
    data_vencimento: str = Field(..., description="Data de vencimento")
    data_base: str = Field(..., description="Data base")
    data_liquidacao: str = Field(..., description="Data de liquidação")
    dias_liquidacao: int = Field(..., description="Dias para liquidação")
    taxa: float = Field(..., description="Taxa de juros (%)")
    quantidade: float = Field(..., description="Quantidade de títulos")
    financeiro: float = Field(..., description="Valor financeiro (R$)")
    pu_d0: float = Field(..., description="Preço unitário à vista")
    pu_termo: Optional[float] = Field(None, description="Preço unitário a termo")
    pu_carregado: Optional[float] = Field(None, description="Preço unitário carregado")
    pu_ajustado: Optional[float] = Field(None, description="Preço unitário ajustado")
    dv01: Optional[float] = Field(None, description="DV01 (sensibilidade à mudança de 1bp)")
    carrego_brl: Optional[float] = Field(None, description="Carregamento em BRL")
    carrego_bps: Optional[float] = Field(None, description="Carregamento em pontos base")
    premio: Optional[float] = Field(None, description="Prêmio sobre DAP")
    cotacao: Optional[float] = Field(None, description="Cotação")
    duration: Optional[float] = Field(None, description="Duration")
    data_vencimento_duration: Optional[str] = Field(None, description="Data de vencimento da duration")
    dias_duration: Optional[int] = Field(None, description="Dias até duration")
    ajuste_dap: Optional[float] = Field(None, description="Ajuste DAP")
    premio_anbima_dap: Optional[float] = Field(None, description="Prêmio ANBIMA DAP")
    hedge_dap: Optional[int] = Field(None, description="Hedge DAP (quantidade de contratos)")
    vna: Optional[float] = Field(None, description="VNA ajustado")
    vna_tesouro: Optional[float] = Field(None, description="VNA Tesouro")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NTNFResponse(BaseModel):
    """Response model para título NTNF (Nota do Tesouro Nacional - Série F)"""
    tipo: str = Field(default="NTNF", description="Tipo do título")
    nome: str = Field(..., description="Nome do título")
    data_vencimento: str = Field(..., description="Data de vencimento")
    data_base: str = Field(..., description="Data base")
    data_liquidacao: str = Field(..., description="Data de liquidação")
    dias_liquidacao: int = Field(..., description="Dias para liquidação")
    taxa: float = Field(..., description="Taxa de juros (%)")
    quantidade: float = Field(..., description="Quantidade de títulos")
    financeiro: float = Field(..., description="Valor financeiro (R$)")
    pu_d0: float = Field(..., description="Preço unitário à vista")
    pu_termo: Optional[float] = Field(None, description="Preço unitário a termo")
    pu_carregado: Optional[float] = Field(None, description="Preço unitário carregado")
    dv01: Optional[float] = Field(None, description="DV01 (sensibilidade à mudança de 1bp)")
    carrego_brl: Optional[float] = Field(None, description="Carregamento em BRL")
    carrego_bps: Optional[float] = Field(None, description="Carregamento em pontos base")
    premio: Optional[float] = Field(None, description="Prêmio sobre DI")
    di: Optional[float] = Field(None, description="Taxa DI de referência")
    ajuste_di: Optional[float] = Field(None, description="Ajuste DI")
    premio_anbima: Optional[float] = Field(None, description="Prêmio ANBIMA")
    hedge_di: Optional[int] = Field(None, description="Hedge DI (quantidade de contratos)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NTNBHedgeDIResponse(BaseModel):
    """Response model para cálculo de hedge DI de um título NTNB"""
    tipo: str = Field(default="NTNB", description="Tipo do título")
    data_vencimento: str = Field(..., description="Data de vencimento do título")
    codigo_di: str = Field(..., description="Código do contrato DI usado")
    quantidade: float = Field(..., description="Quantidade de títulos NTNB")
    financeiro: float = Field(..., description="Valor financeiro da posição (R$)")
    dv01_ntnb: float = Field(..., description="DV01 do título NTNB")
    hedge_di: int = Field(..., description="Quantidade de contratos DI necessários para hedge")
    ajuste_di: Optional[float] = Field(None, description="Ajuste DI do contrato usado")


class EquivalenciaResponse(BaseModel):
    """Response model para cálculo de equivalência"""
    titulo1: str = Field(..., description="Tipo do primeiro título")
    venc1: str = Field(..., description="Vencimento do primeiro título")
    titulo2: str = Field(..., description="Tipo do segundo título")
    venc2: str = Field(..., description="Vencimento do segundo título")
    qtd1: float = Field(..., description="Quantidade do primeiro título")
    equivalencia: float = Field(..., description="Quantidade equivalente do segundo título")
    criterio: str = Field(..., description="Critério usado para cálculo")


class ErrorResponse(BaseModel):
    """Modelo para respostas de erro"""
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
