from __future__ import annotations

from app.common.exceptions import ValidationException
from app.modules.accounting.models.fiscal import FiscalYear
from app.modules.accounting.schemas.fiscal import FiscalYearCreate
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_fiscal_year(db: Session, payload: FiscalYearCreate) -> FiscalYear:
    if payload.end_date <= payload.start_date:
        raise ValidationException("Fiscal year end_date must be greater than start_date.")

    existing = list(db.scalars(select(FiscalYear)).all())
    for item in existing:
        overlaps = payload.start_date <= item.end_date and payload.end_date >= item.start_date
        if overlaps:
            raise ValidationException(f"Fiscal year overlaps with existing fiscal year: {item.name}.")

    fy = FiscalYear(
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_active=payload.is_active,
    )
    db.add(fy)
    db.commit()
    db.refresh(fy)
    return fy
