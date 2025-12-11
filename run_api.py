"""
Script para iniciar a API FastAPI com uvicorn.

IMPORTANTE: Usar workers=1 para carteiras em memória funcionarem corretamente.
Com múltiplos workers, cada worker tem sua própria memória e as carteiras
criadas em um worker não ficam disponíveis nos outros.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        workers=1,  # Usar 1 worker para carteiras em memória funcionarem corretamente
        reload=False,
        log_level="info"
    )
