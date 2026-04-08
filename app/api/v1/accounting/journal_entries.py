from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.accounting.journal_entry import JournalEntryCreate, JournalEntryRead
from app.services.accounting.journal_entry_service import JournalEntryService

router = APIRouter(prefix="/accounting/je", tags=["Accounting - Journal Entries"])


def get_current_tenant_id() -> str:
    # TODO: replace with real tenant resolution from auth/session
    return "00000000-0000-0000-0000-000000000001"


@router.get("", response_model=list[JournalEntryRead])
async def list_journal_entries(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    service = JournalEntryService(db, tenant_id)
    return await service.list_journal_entries()


@router.post("", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    service = JournalEntryService(db, tenant_id)
    try:
        journal_entry = await service.create_journal_entry(payload)
        await db.commit()
        return journal_entry
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        await db.rollback()
        raise
