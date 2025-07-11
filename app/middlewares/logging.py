from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from loguru import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Method: {request.method}\n" \
                    f"URL: {request.url}\n")

        logger.info("Request headers:\n")
        for key in request.headers.keys():
            logger.info(f"{key}: {request.headers[key]}\n")
        if request.query_params:
            logger.info(f"Query params: {request.query_params}\n\n")

        response = await call_next(request)
        
        logger.info(f"Status code: {response.status_code}\n" \
                    f"Response Media-Type: {response.media_type}\n")
        logger.info("Response headers:\n")
        for key in response.headers.keys():
            logger.info(f"{key}: {response.headers[key]}\n")
        return response