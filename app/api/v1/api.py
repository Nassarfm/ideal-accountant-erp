from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.modules.accounting.api.router import router as accounting_router
from app.modules.accounting.api.module4_routes import router as accounting_reports_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(accounting_router)
api_router.include_router(accounting_reports_router)
