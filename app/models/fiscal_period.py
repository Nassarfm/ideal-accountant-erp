from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.accounting_enums import FiscalPeriodStatus


class FiscalPeriod(Base):
    __tablename__ = "fiscal_periods"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "fiscal_year",
            "period_no",
            name="uq_fiscal_periods_tenant_year_period",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    period_no: Mapped[int] = mapped_column(Integer, nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=FiscalPeriodStatus.OPEN.value)

    locks: Mapped[list["FiscalLock"]] = relationship(
        "FiscalLock",
        back_populates="period",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<FiscalPeriod {self.fiscal_year}-{self.period_no}>"
