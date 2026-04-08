from fastapi import APIRouter

from app.api.v1.accounting.coa import router as coa_router
from app.api.v1.accounting.journal_entries import router as journal_entries_router
from app.api.v1.accounting.fiscal import router as fiscal_router
from app.api.v1.accounting.reports import router as reports_router

api_router = APIRouter()

api_router.include_router(coa_router)
api_router.include_router(journal_entries_router)
api_router.include_router(fiscal_router)
api_router.include_router(reports_router)
