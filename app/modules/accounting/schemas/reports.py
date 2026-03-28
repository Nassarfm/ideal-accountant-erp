from decimal import Decimal
from datetime import date
from pydantic import BaseModel

class LedgerEntryRead(BaseModel):
    id: int
    entry_number: str
    entry_date: date
    debit_amount: Decimal
    credit_amount: Decimal
    subledger_type: str
    subledger_reference: str | None = None
    class Config:
        from_attributes = True

class TrialBalanceLineRead(BaseModel):
    account_id: int
    account_code: str
    account_name: str
    debit_total: Decimal
    credit_total: Decimal
    closing_balance: Decimal
    class Config:
        from_attributes = True

class TrialBalanceResponse(BaseModel):
    fiscal_year_id: int
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool
    lines: list[TrialBalanceLineRead]
