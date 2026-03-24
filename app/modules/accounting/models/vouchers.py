from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VoucherType(Base):
    __tablename__ = "voucher_types"
    __table_args__ = (UniqueConstraint("code", name="uq_voucher_type_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    reset_by_fiscal_year: Mapped[bool] = mapped_column(Boolean, default=True)
    padding: Mapped[int] = mapped_column(Integer, default=5)


class DocumentSequence(Base):
    __tablename__ = "document_sequences"
    __table_args__ = (UniqueConstraint("voucher_type_id", "fiscal_year_id", name="uq_document_sequence_voucher_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    voucher_type_id: Mapped[int] = mapped_column(ForeignKey("voucher_types.id", ondelete="CASCADE"), index=True)
    fiscal_year_id: Mapped[int] = mapped_column(ForeignKey("fiscal_years.id", ondelete="CASCADE"), index=True)
    current_number: Mapped[int] = mapped_column(Integer, default=0)
