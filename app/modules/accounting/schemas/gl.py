from datetime import date
from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional


class GLRow(BaseModel):
    entry_date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    debit: Decimal
    credit: Decimal
    balance: Decimal


class GLResponse(BaseModel):
    account_code: str
    account_name: Optional[str] = None
    opening_balance: Decimal
    closing_balance: Decimal
    rows: List[GLRow]