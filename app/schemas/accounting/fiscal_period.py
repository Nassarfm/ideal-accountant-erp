from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FiscalPeriodCreate(BaseModel):
    fiscal_year: int
    period_no: int
    start_date: date
    end_date: date
    status: str = "open"


class FiscalPeriodRead(BaseModel):
    id: UUID
    tenant_id: UUID
    fiscal_year: int
    period_no: int
    start_date: date
    end_date: date
    status: str

    model_config = ConfigDict(from_attributes=True)


class FiscalLockCreate(BaseModel):
    period_id: UUID
    lock_type: str = "soft"
    reason: Optional[str] = None
