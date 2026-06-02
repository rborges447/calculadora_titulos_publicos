"""
Endpoints para explorer de consultas ao banco gold (Spec 003).
"""

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Response

from api.logging_config import get_logger
from api.models import (
    CatalogoConsultasResponse,
    ConsultaDbRequest,
    ConsultaHistoricoResponse,
    ConsultasDbStatusResponse,
    FonteConsultaItem,
)
from titulospub.dados.consultas_db import (
    BancoIndisponivelError,
    ColunasInvalidasError,
    IntervaloSemDadosError,
    LimiteExportacaoError,
    TabelaAusenteNoBancoError,
    TabelaDesconhecidaError,
    consultar,
    exportar_csv,
    listar_catalogo,
)
from titulospub.dados.db_reader import get_db_path

router = APIRouter(prefix="/consultas-db", tags=["Consultas DB"])
logger = get_logger("api.routers.consultas_db")


def _consulta_kwargs(request: ConsultaDbRequest) -> dict:
    return request.model_dump()


@router.get(
    "/catalogo",
    response_model=CatalogoConsultasResponse,
    summary="Catálogo de fontes consultáveis",
)
def obter_catalogo() -> CatalogoConsultasResponse:
    """Retorna metadados de todas as fontes do explorer (máscara whitelist)."""
    fontes = [FonteConsultaItem.model_validate(f) for f in listar_catalogo()]
    return CatalogoConsultasResponse(fontes=fontes)


@router.get(
    "/status",
    response_model=ConsultasDbStatusResponse,
    summary="Status do SQLite gold",
)
def obter_status() -> ConsultasDbStatusResponse:
    """Verifica caminho e existência do banco sem abrir conexão."""
    path = get_db_path()
    return ConsultasDbStatusResponse(
        db_path=str(path),
        db_existe=path.is_file(),
        total_fontes=len(listar_catalogo()),
    )


@router.post(
    "/consultar",
    response_model=ConsultaHistoricoResponse,
    summary="Consultar dados do gold (preview)",
)
def post_consultar(request: ConsultaDbRequest) -> ConsultaHistoricoResponse:
    """Consulta gold com preview limitado; regras de negócio no domínio."""
    try:
        resultado = consultar(**_consulta_kwargs(request))
        return ConsultaHistoricoResponse.model_validate(asdict(resultado))
    except TabelaDesconhecidaError as e:
        logger.warning("Tabela desconhecida: %s", e.tabela)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (ColunasInvalidasError, ValueError, LimiteExportacaoError, IntervaloSemDadosError) as e:
        logger.warning("Consulta inválida: %s", e)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except BancoIndisponivelError as e:
        logger.warning("Banco indisponível: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e
    except TabelaAusenteNoBancoError as e:
        logger.warning("Tabela ausente no SQLite: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.error("Erro ao consultar banco: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao consultar o banco de dados.",
        ) from e


@router.post(
    "/exportar-csv",
    summary="Exportar consulta em CSV",
    responses={200: {"content": {"text/csv": {}}}},
)
def post_exportar_csv(request: ConsultaDbRequest) -> Response:
    """Exporta o recorte completo em CSV UTF-8 com BOM."""
    try:
        conteudo, nome = exportar_csv(**_consulta_kwargs(request))
        return Response(
            content=conteudo,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{nome}"'},
        )
    except TabelaDesconhecidaError as e:
        logger.warning("Tabela desconhecida: %s", e.tabela)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (ColunasInvalidasError, ValueError, LimiteExportacaoError, IntervaloSemDadosError) as e:
        logger.warning("Exportação inválida: %s", e)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except BancoIndisponivelError as e:
        logger.warning("Banco indisponível: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e
    except TabelaAusenteNoBancoError as e:
        logger.warning("Tabela ausente no SQLite: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.error("Erro ao exportar CSV: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao exportar CSV.",
        ) from e
