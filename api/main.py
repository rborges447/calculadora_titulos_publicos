"""
API FastAPI para cálculo de títulos públicos brasileiros
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from titulospub.dados.orquestrador import VariaveisMercado

from .logging_config import get_logger
from .middleware.metrics import MetricsMiddleware
from .routers import carteiras, consultas_db, equivalencia, lft, ltn, ntnb, ntnf, vencimentos
from .utils import marcar_atualizado, precisa_atualizar_mercado, resolver_data_mercado

# Logger para este módulo
logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: executa na inicialização e finalização da API
    Atualiza variáveis de mercado uma vez por dia na inicialização
    """
    # Startup: Verificar e atualizar variáveis de mercado se necessário
    if precisa_atualizar_mercado():
        print("🔄 Atualizando variáveis de mercado (primeira vez hoje)...")
        logger.info("Atualizando variáveis de mercado (primeira vez hoje)")
        try:
            vm = VariaveisMercado()
            data_ref = resolver_data_mercado()
            vm.atualizar_tudo(data_ref, verbose=True)
            marcar_atualizado()
            print("✅ Variáveis de mercado atualizadas com sucesso!")
            logger.info("Variáveis de mercado atualizadas com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao atualizar variáveis de mercado: {e}")
            print("   Usando dados em cache...")
            logger.warning(f"Erro ao atualizar variáveis de mercado: {e}, usando cache")
    else:
        print("ℹ️ Variáveis de mercado já atualizadas hoje. Usando dados em cache.")
        logger.info("Variáveis de mercado já atualizadas hoje, usando cache")
    
    yield
    
    # Shutdown: limpeza se necessário
    pass

# Criar instância da aplicação FastAPI
app = FastAPI(
    title="API de Títulos Públicos",
    description="API para cálculo e análise de títulos públicos brasileiros (LTN, LFT, NTNB, NTNF)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Adicionar middleware de métricas (deve vir antes do CORS para capturar todas as requisições)
app.add_middleware(MetricsMiddleware)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(ltn.router)
app.include_router(lft.router)
app.include_router(ntnb.router)
app.include_router(ntnf.router)
app.include_router(equivalencia.router)
app.include_router(vencimentos.router)
app.include_router(carteiras.router)
app.include_router(consultas_db.router)


@app.get("/", tags=["Root"])
def root():
    """Endpoint raiz da API"""
    return {
        "message": "API de Títulos Públicos Brasileiros",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "titulos": {
                "ltn": "POST /titulos/ltn",
                "lft": "POST /titulos/lft",
                "ntnb": {
                    "criar": "POST /titulos/ntnb",
                    "hedge_di": "POST /titulos/ntnb/hedge-di"
                },
                "ntnf": "POST /titulos/ntnf"
            },
            "equivalencia": "POST /equivalencia",
            "consultas_db": {
                "catalogo": "GET /consultas-db/catalogo",
                "status": "GET /consultas-db/status",
                "consultar": "POST /consultas-db/consultar",
                "exportar_csv": "POST /consultas-db/exportar-csv",
            },
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint de health check básico.
    
    Retorna status da API e última atualização de mercado.
    """
    from .utils import get_ultima_atualizacao
    
    return {
        "status": "healthy",
        "ultima_atualizacao_mercado": get_ultima_atualizacao()
    }


@app.get("/ready", tags=["Health"])
def readiness_check():
    """
    Endpoint de readiness check.
    
    Verifica se a API está pronta para receber requisições.
    Útil para load balancers e orquestradores (Kubernetes, etc).
    
    Retorna:
        - ready: True se API está pronta
        - workers: Número de workers (sempre 1 atualmente devido a limitação de carteiras)
        - cache_status: Status do cache (ok se disponível)
    """
    from pathlib import Path
    from .utils import get_ultima_atualizacao
    
    # Verificar se cache está disponível (arquivo de controle existe)
    cache_ok = Path("api/.ultima_atualizacao.json").exists()
    
    return {
        "ready": True,  # API sempre está pronta (usa cache/backup se necessário)
        "workers": 1,  # Atualmente limitado a 1 worker devido a carteiras em memória
        "cache_status": "ok" if cache_ok else "unavailable",
        "ultima_atualizacao_mercado": get_ultima_atualizacao()
    }


@app.get("/live", tags=["Health"])
def liveness_check():
    """
    Endpoint de liveness check.
    
    Verifica se o processo está vivo.
    Útil para orquestradores (Kubernetes, etc) detectarem processos travados.
    
    Retorna:
        - alive: True se processo está vivo
        - timestamp: Timestamp atual em ISO format
    """
    from datetime import datetime
    
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/atualizar-mercado", tags=["Admin"])
def forcar_atualizacao_mercado(
    data: str | None = Query(
        None,
        description="Data de referência YYYY-MM-DD (padrão: D-1 útil)",
    ),
):
    """
    Força a atualização das variáveis de mercado (admin)
    Útil para atualizar manualmente se necessário
    """
    from .utils import get_ultima_atualizacao, marcar_atualizado

    try:
        data_ref = resolver_data_mercado(data)
        print(f"🔄 Forçando atualização de variáveis de mercado (data={data_ref.date()})...")
        logger.info(
            "Forçando atualização de variáveis de mercado (endpoint admin, data=%s)",
            data_ref.date(),
        )
        vm = VariaveisMercado()
        vm.atualizar_tudo(data_ref, verbose=True)
        marcar_atualizado()
        logger.info("Variáveis de mercado atualizadas com sucesso (endpoint admin)")
        return {
            "status": "success",
            "message": "Variáveis de mercado atualizadas com sucesso",
            "data": get_ultima_atualizacao(),
            "data_referencia": data_ref.strftime("%Y-%m-%d"),
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar variáveis de mercado (endpoint admin): {e}")
        return {
            "status": "error",
            "message": f"Erro ao atualizar: {str(e)}"
        }
