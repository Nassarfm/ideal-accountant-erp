from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.modules.accounting.schemas.common import ORMBaseSchema


class LedgerEntryRead(ORMBaseSchema):
    id: int
    journal_entry_id: int
    journal_entry_line_id: int
    entry_number: str
    entry_date: date
    fiscal_year_id: int
    voucher_type_id: int | None = None
    legal_entity_id: int
    branch_id: int
    account_id: int
    subledger_type: str
    subledger_reference: str | None = None
    cost_center_id: int | None = None
    department_id: int | None = None
    project_id: int | None = None
    geographic_region_id: int | None = None
    business_line_id: int | None = None
    reserve_dimension_9_id: int | None = None
    reserve_dimension_10_id: int | None = None
    debit_amount: Decimal
    credit_amount: Decimal
    posted_at: datetime


class TrialBalanceItem(ORMBaseSchema):
    account_id: int
    account_code: str
    account_name_ar: str
    account_name_en: str | None = None
    total_debit: Decimal
    total_credit: Decimal
    balance: Decimal


class TrialBalanceResponse(ORMBaseSchema):
    fiscal_year_id: int
    items: list[TrialBalanceItem] = []
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool