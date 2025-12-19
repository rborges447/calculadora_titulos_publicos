"""
Middleware de métricas para capturar latência e informações de requisições.

Este middleware adiciona observabilidade sem alterar o comportamento das requisições.
Apenas registra informações de latência e status HTTP.
"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.logging_config import get_logger

logger = get_logger("api.metrics")


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para capturar métricas de latência e status de requisições.

    Registra:
    - Método HTTP
    - Caminho da requisição
    - Latência em segundos
    - Status HTTP da resposta

    Não altera o comportamento das requisições, apenas observa.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição e captura métricas.

        Args:
            request: Requisição HTTP
            call_next: Próximo middleware/handler na cadeia

        Returns:
            Resposta HTTP
        """
        start_time = time.time()

        # Processa a requisição
        response = await call_next(request)

        # Calcula latência
        duration = time.time() - start_time

        # Registra métricas (apenas observação, não altera comportamento)
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{duration:.3f}s - Status: {response.status_code}"
        )

        return response

