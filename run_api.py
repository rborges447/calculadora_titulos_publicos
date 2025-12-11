"""
Script para iniciar a API FastAPI com uvicorn usando 4 workers
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=False,  # Desabilitar reload em produção com múltiplos workers
        log_level="info"
    )
