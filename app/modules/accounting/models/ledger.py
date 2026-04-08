from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    journal_entry_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    journal_entry_line_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    legal_entity_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    branch_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    account_id: Mapped[str] = mapped_column(Text, nullable=False)
    account_code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    debit: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    credit: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<LedgerEntry account_code={self.account_code} entry_date={self.entry_date}>"