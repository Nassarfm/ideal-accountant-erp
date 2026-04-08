from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JournalEntryLineCreate(BaseModel):
    account_id: UUID
    description: Optional[str] = None
    debit: float = 0
    credit: float = 0


class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str
    reference: Optional[str] = None
    je_type: str = "GJE"
    lines: list[JournalEntryLineCreate]


class JournalEntryLineRead(BaseModel):
    id: UUID
    journal_entry_id: UUID
    line_no: int
    account_id: UUID
    description: Optional[str] = None
    debit: float
    credit: float

    model_config = ConfigDict(from_attributes=True)


class JournalEntryRead(BaseModel):
    id: UUID
    tenant_id: UUID
    entry_no: str
    entry_date: date
    description: str
    reference: Optional[str] = None
    je_type: str
    status: str
    total_debit: float
    total_credit: float
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    posted_at: Optional[datetime] = None
    posted_by: Optional[UUID] = None
    reversed_from_id: Optional[UUID] = None
    lines: list[JournalEntryLineRead] = []

    model_config = ConfigDict(from_attributes=True)
