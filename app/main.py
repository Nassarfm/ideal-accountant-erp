from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.common.exceptions import ValidationException
from app.core.config import settings

# ✅ إضافة GL Router
from app.modules.accounting.api.gl_router import router as gl_router


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        debug=settings.app_debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(_: Request, exc: ValidationException) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message})

    @app.get("/", tags=["Root"])
    def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} is running", "docs": "/docs"}

    # ✅ الراوتر الرئيسي
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # ✅ إضافة General Ledger Router
    app.include_router(gl_router, prefix=settings.api_v1_prefix)

    return app


app = create_application()