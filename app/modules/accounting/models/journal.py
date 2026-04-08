from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), nullable=True, index=True)
    entry_date = Column(Date, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    reference = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, server_default="DRAFT", index=True)

    fiscal_year_id = Column(Integer, ForeignKey("fiscal_years.id", ondelete="RESTRICT"), nullable=False, index=True)
    voucher_type_id = Column(Integer, ForeignKey("voucher_types.id", ondelete="RESTRICT"), nullable=True, index=True)
    legal_entity_id = Column(Integer, ForeignKey("legal_entities.id", ondelete="RESTRICT"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False, index=True)

    currency_code = Column(String(10), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)

    lines = relationship(
        "app.modules.accounting.models.journal.JournalEntryLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )

    # تم حذف ledger_entries relationship مؤقتًا
    # لأن جدول ledger_entries الحالي لا يحتوي ForeignKey فعلي
    # ومع وجود relationship بدون FK يحصل:
    # sqlalchemy.exc.NoForeignKeysError


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)

    line_number = Column(Integer, nullable=False)

    legal_entity_id = Column(Integer, ForeignKey("legal_entities.id", ondelete="RESTRICT"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False, index=True)

    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)

    line_description = Column("description", String(500), nullable=True)

    debit_amount = Column("debit", Numeric(18, 2), nullable=False, server_default="0")
    credit_amount = Column("credit", Numeric(18, 2), nullable=False, server_default="0")

    subledger_type = Column(String(50), nullable=False, server_default="NONE")
    subledger_reference = Column(String(100), nullable=True)

    cost_center_id = Column(Integer, ForeignKey("cost_centers.id", ondelete="RESTRICT"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=True)
    geographic_region_id = Column(Integer, ForeignKey("geographic_regions.id", ondelete="RESTRICT"), nullable=True)
    business_line_id = Column(Integer, ForeignKey("business_lines.id", ondelete="RESTRICT"), nullable=True)
    reserve_dimension_9_id = Column(Integer, ForeignKey("reserve_dimension_9_values.id", ondelete="RESTRICT"), nullable=True)
    reserve_dimension_10_id = Column(Integer, ForeignKey("reserve_dimension_10_values.id", ondelete="RESTRICT"), nullable=True)

    journal_entry = relationship(
        "app.modules.accounting.models.journal.JournalEntry",
        back_populates="lines",
    )

    account = relationship("app.modules.accounting.models.accounts.Account")