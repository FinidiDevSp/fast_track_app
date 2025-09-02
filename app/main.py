from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# IMPORTANTE: importa modelos para que estén en metadata
from app.api.v1.routes import api_router
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # <- crea tablas antes de aceptar tráfico
    yield
    # aquí podrías cerrar conexiones si hiciera falta


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Consistent error schema handler
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        from fastapi import HTTPException

        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"code": exc.status_code, "message": exc.detail},
            )
        return JSONResponse(
            status_code=500, content={"code": 500, "message": "Internal Server Error"}
        )

    return app


app = create_app()
