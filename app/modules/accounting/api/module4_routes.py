from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.accounting.schemas.reports import LedgerEntryRead, TrialBalanceResponse
from app.modules.accounting.services.journal import post_journal_entry
from app.modules.accounting.services.reports import get_ledger_for_account, get_trial_balance

router = APIRouter(prefix="/accounting", tags=["Accounting Reports"])


@router.post("/journal-entries/{journal_entry_id}/post", summary="Post Journal Entry")
def post_journal_entry_endpoint(journal_entry_id: int, db: Session = Depends(get_db)):
    return post_journal_entry(db, journal_entry_id)


@router.get("/ledger/{account_code}", response_model=list[LedgerEntryRead], summary="Get Account Ledger")
def get_account_ledger(account_code: str, db: Session = Depends(get_db)):
    return get_ledger_for_account(db, account_code)


@router.get("/trial-balance", response_model=TrialBalanceResponse, summary="Get Trial Balance")
def get_trial_balance_endpoint(fiscal_year_id: int, db: Session = Depends(get_db)):
    return get_trial_balance(db, fiscal_year_id)