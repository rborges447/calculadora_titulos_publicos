"""
API FastAPI para cálculo de títulos públicos brasileiros
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import ntnb, ltn, lft, ntnf, equivalencia
from .utils import precisa_atualizar_mercado, marcar_atualizado
from titulospub.dados.orquestrador import VariaveisMercado


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: executa na inicialização e finalização da API
    Atualiza variáveis de mercado uma vez por dia na inicialização
    """
    # Startup: Verificar e atualizar variáveis de mercado se necessário
    if precisa_atualizar_mercado():
        print("🔄 Atualizando variáveis de mercado (primeira vez hoje)...")
        try:
            vm = VariaveisMercado()
            # Usar o método atualizar_tudo() que já faz tudo automaticamente
            vm.atualizar_tudo(verbose=True)
            marcar_atualizado()
            print("✅ Variáveis de mercado atualizadas com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao atualizar variáveis de mercado: {e}")
            print("   Usando dados em cache...")
    else:
        print("ℹ️ Variáveis de mercado já atualizadas hoje. Usando dados em cache.")
    
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
            "equivalencia": "POST /equivalencia"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de health check"""
    from .utils import get_ultima_atualizacao
    return {
        "status": "healthy",
        "ultima_atualizacao_mercado": get_ultima_atualizacao()
    }


@app.post("/atualizar-mercado", tags=["Admin"])
def forcar_atualizacao_mercado():
    """
    Força a atualização das variáveis de mercado (admin)
    Útil para atualizar manualmente se necessário
    """
    from .utils import marcar_atualizado, get_ultima_atualizacao
    from titulospub.dados.orquestrador import VariaveisMercado
    
    try:
        print("🔄 Forçando atualização de variáveis de mercado...")
        vm = VariaveisMercado()
        vm.atualizar_tudo(verbose=True)
        marcar_atualizado()
        return {
            "status": "success",
            "message": "Variáveis de mercado atualizadas com sucesso",
            "data": get_ultima_atualizacao()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao atualizar: {str(e)}"
        }
