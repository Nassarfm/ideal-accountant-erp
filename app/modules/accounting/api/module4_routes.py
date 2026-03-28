from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.accounting.schemas.reports import LedgerEntryRead, TrialBalanceResponse
from app.modules.accounting.services.posting_engine import post_journal_entry
from app.modules.accounting.services.reports import get_ledger_for_account, get_trial_balance

router = APIRouter(prefix="/api/v1/accounting", tags=["Accounting Reports"])

@router.post("/journal-entries/{journal_entry_id}/post", summary="Post Journal Entry")
async def post_journal_entry_endpoint(journal_entry_id: int, db: AsyncSession = Depends(get_db)):
    journal_entry = await post_journal_entry(db, journal_entry_id)
    return {"id": journal_entry.id, "status": journal_entry.status, "message": "Journal entry posted successfully."}

@router.get("/ledger/{account_code}", response_model=list[LedgerEntryRead], summary="Get Account Ledger")
async def get_account_ledger(account_code: str, db: AsyncSession = Depends(get_db)):
    return await get_ledger_for_account(db, account_code)

@router.get("/trial-balance", response_model=TrialBalanceResponse, summary="Get Trial Balance")
async def get_trial_balance_endpoint(fiscal_year_id: int, db: AsyncSession = Depends(get_db)):
    return await get_trial_balance(db, fiscal_year_id)
