from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Numeric, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    __table_args__ = (
        CheckConstraint("debit >= 0", name="ck_journal_entry_lines_debit_nonnegative"),
        CheckConstraint("credit >= 0", name="ck_journal_entry_lines_credit_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    line_no: Mapped[int] = mapped_column(Integer, nullable=False)

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    debit: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    credit: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    journal_entry: Mapped["JournalEntry"] = relationship(
        "JournalEntry",
        back_populates="lines",
    )
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="journal_lines",
    )

    def __repr__(self) -> str:
        return f"<JournalEntryLine line_no={self.line_no}>"
