from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.common.enums import JournalEntryStatus, SubledgerType
from app.modules.accounting.schemas.common import ORMBaseSchema


class JournalEntryLineCreate(BaseModel):
    legal_entity_id: int
    branch_id: int
    account_id: int
    subledger_type: SubledgerType = SubledgerType.NONE
    subledger_reference: str | None = None
    cost_center_id: int | None = None
    department_id: int | None = None
    project_id: int | None = None
    geographic_region_id: int | None = None
    business_line_id: int | None = None
    reserve_dimension_9_id: int | None = None
    reserve_dimension_10_id: int | None = None
    line_description: str | None = None
    debit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)

    @model_validator(mode="after")
    def validate_line_amounts(self) -> "JournalEntryLineCreate":
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("Either debit_amount or credit_amount must be greater than zero.")
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("A journal line cannot have both debit and credit amounts.")
        return self


class JournalEntryCreate(BaseModel):
    voucher_type_id: int
    fiscal_year_id: int
    entry_date: date
    reference: str | None = None
    currency_code: str | None = "SAR"
    description: str | None = None
    lines: list[JournalEntryLineCreate]


class JournalEntryLineRead(ORMBaseSchema):
    id: int
    line_number: int
    legal_entity_id: int
    branch_id: int
    account_id: int
    subledger_type: SubledgerType
    subledger_reference: str | None
    cost_center_id: int | None
    department_id: int | None
    project_id: int | None
    geographic_region_id: int | None
    business_line_id: int | None
    reserve_dimension_9_id: int | None
    reserve_dimension_10_id: int | None
    line_description: str | None
    debit_amount: Decimal
    credit_amount: Decimal


class JournalEntryRead(ORMBaseSchema):
    id: int
    entry_number: str | None = None
    voucher_type_id: int | None = None
    fiscal_year_id: int
    entry_date: date
    reference: str | None = None
    currency_code: str | None = None
    description: str | None = None
    status: JournalEntryStatus
    created_at: datetime | None = None
    approved_at: datetime | None = None
    posted_at: datetime | None = None
    lines: list[JournalEntryLineRead] = []


class LedgerEntryRead(ORMBaseSchema):
    id: int
    journal_entry_id: int
    journal_entry_line_id: int
    entry_number: str
    entry_date: date
    fiscal_year_id: int
    voucher_type_id: int | None
    legal_entity_id: int
    branch_id: int
    account_id: int
    subledger_type: str
    subledger_reference: str | None
    cost_center_id: int | None
    department_id: int | None
    project_id: int | None
    geographic_region_id: int | None
    business_line_id: int | None
    reserve_dimension_9_id: int | None
    reserve_dimension_10_id: int | None
    debit_amount: Decimal
    credit_amount: Decimal
    posted_at: datetime