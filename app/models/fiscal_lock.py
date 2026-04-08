from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.accounting_enums import LockType


class FiscalLock(Base):
    __tablename__ = "fiscal_locks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fiscal_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lock_type: Mapped[str] = mapped_column(String(20), nullable=False, default=LockType.SOFT.value)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    period: Mapped["FiscalPeriod"] = relationship(
        "FiscalPeriod",
        back_populates="locks",
    )

    def __repr__(self) -> str:
        return f"<FiscalLock period_id={self.period_id} type={self.lock_type}>"
