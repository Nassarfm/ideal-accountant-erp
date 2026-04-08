from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.accounting.fiscal_repository import FiscalRepository

router = APIRouter(prefix="/accounting/fiscal-periods", tags=["Accounting - Fiscal"])


def get_current_tenant_id() -> str:
    # TODO: replace with real tenant resolution from auth/session
    return "00000000-0000-0000-0000-000000000001"


@router.get("")
async def list_periods(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    repo = FiscalRepository(db)
    return await repo.list_periods(tenant_id)
