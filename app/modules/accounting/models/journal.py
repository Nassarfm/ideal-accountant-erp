from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import JournalEntryStatus, SubledgerType
from app.db.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entry_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    voucher_type_id: Mapped[int | None] = mapped_column(ForeignKey("voucher_types.id", ondelete="RESTRICT"), nullable=True, index=True)
    fiscal_year_id: Mapped[int] = mapped_column(ForeignKey("fiscal_years.id", ondelete="RESTRICT"), index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[JournalEntryStatus] = mapped_column(Enum(JournalEntryStatus, name="journal_entry_status"), default=JournalEntryStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lines: Mapped[list["JournalEntryLine"]] = relationship(back_populates="journal_entry", cascade="all, delete-orphan")
    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="journal_entry", cascade="all, delete-orphan")


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journal_entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id", ondelete="CASCADE"), index=True)
    line_number: Mapped[int] = mapped_column(Integer)
    legal_entity_id: Mapped[int] = mapped_column(ForeignKey("legal_entities.id", ondelete="RESTRICT"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="RESTRICT"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True)
    cost_center_id: Mapped[int | None] = mapped_column(ForeignKey("cost_centers.id", ondelete="RESTRICT"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"), nullable=True)
    geographic_region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id", ondelete="RESTRICT"), nullable=True)
    business_line_id: Mapped[int | None] = mapped_column(ForeignKey("business_lines.id", ondelete="RESTRICT"), nullable=True)
    reserve_dimension_9_id: Mapped[int | None] = mapped_column(ForeignKey("reserve_dimension_9_values.id", ondelete="RESTRICT"), nullable=True)
    reserve_dimension_10_id: Mapped[int | None] = mapped_column(ForeignKey("reserve_dimension_10_values.id", ondelete="RESTRICT"), nullable=True)
    subledger_type: Mapped[SubledgerType] = mapped_column(Enum(SubledgerType, name="journal_line_subledger_type"), default=SubledgerType.NONE)
    subledger_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    line_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="lines")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journal_entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id", ondelete="CASCADE"), index=True)
    journal_entry_line_id: Mapped[int] = mapped_column(ForeignKey("journal_entry_lines.id", ondelete="CASCADE"), index=True)
    entry_number: Mapped[str] = mapped_column(String(50), index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    fiscal_year_id: Mapped[int] = mapped_column(ForeignKey("fiscal_years.id", ondelete="RESTRICT"), index=True)
    voucher_type_id: Mapped[int | None] = mapped_column(ForeignKey("voucher_types.id", ondelete="RESTRICT"), nullable=True, index=True)
    legal_entity_id: Mapped[int] = mapped_column(ForeignKey("legal_entities.id", ondelete="RESTRICT"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id", ondelete="RESTRICT"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True)
    subledger_type: Mapped[str] = mapped_column(String(20), default="NONE")
    subledger_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_center_id: Mapped[int | None] = mapped_column(ForeignKey("cost_centers.id", ondelete="RESTRICT"), nullable=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"), nullable=True)
    geographic_region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id", ondelete="RESTRICT"), nullable=True)
    business_line_id: Mapped[int | None] = mapped_column(ForeignKey("business_lines.id", ondelete="RESTRICT"), nullable=True)
    reserve_dimension_9_id: Mapped[int | None] = mapped_column(ForeignKey("reserve_dimension_9_values.id", ondelete="RESTRICT"), nullable=True)
    reserve_dimension_10_id: Mapped[int | None] = mapped_column(ForeignKey("reserve_dimension_10_values.id", ondelete="RESTRICT"), nullable=True)
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="ledger_entries")
