from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.accounting.account import AccountCreate, AccountRead
from app.services.accounting.account_service import AccountService

router = APIRouter(prefix="/accounting/accounts", tags=["Accounting - COA"])


def get_current_tenant_id() -> str:
    # TODO: replace with real tenant resolution from auth/session
    return "00000000-0000-0000-0000-000000000001"


@router.get("", response_model=list[AccountRead])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    service = AccountService(db, tenant_id)
    return await service.list_accounts()


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    service = AccountService(db, tenant_id)
    try:
        account = await service.create_account(payload)
        await db.commit()
        return account
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        await db.rollback()
        raise
