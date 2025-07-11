from fastapi import FastAPI
import uvicorn

from app.routers import complaint_router
from app.middlewares import LoggingMiddleware

app = FastAPI()

app.include_router(complaint_router)

app.add_middleware(LoggingMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоперезагрузка для разработки
        log_level="debug",
    )