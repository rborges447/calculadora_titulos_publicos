"""
Script para iniciar a API FastAPI com uvicorn.

NOTA SOBRE WORKERS:
- Com workers=1: Carteiras funcionam corretamente (estado em memória compartilhado)
- Com workers>1: Carteiras não funcionam corretamente (cada worker tem memória separada)
- Para produção com múltiplos workers, migre carteiras para banco de dados ou Redis

Para desenvolvimento/testes: workers=1 é aceitável
Para produção escalável: use workers>1 e migre carteiras para persistência externa
"""
import os
import uvicorn

if __name__ == "__main__":
    # Permitir configurar workers via variável de ambiente
    workers = int(os.getenv("API_WORKERS", "1"))
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        workers=workers,
        reload=False,
        log_level="info"
    )
