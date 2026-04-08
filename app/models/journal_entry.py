from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.accounting_enums import JournalEntryStatus, JournalEntryType


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    entry_no: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    je_type: Mapped[str] = mapped_column(String(20), nullable=False, default=JournalEntryType.GJE.value)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=JournalEntryStatus.DRAFT.value)

    total_debit: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    total_credit: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    reversed_from_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True,
    )

    lines: Mapped[list["JournalEntryLine"]] = relationship(
        "JournalEntryLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )

    reversed_from: Mapped[Optional["JournalEntry"]] = relationship(
        "JournalEntry",
        remote_side="JournalEntry.id",
    )

    def __repr__(self) -> str:
        return f"<JournalEntry entry_no={self.entry_no} status={self.status}>"

    @property
    def je_type_enum(self) -> JournalEntryType:
        return JournalEntryType(self.je_type)

    @property
    def status_enum(self) -> JournalEntryStatus:
        return JournalEntryStatus(self.status)
