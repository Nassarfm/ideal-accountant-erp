from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import AccountMainType, DimensionCode, FinancialStatementType, NormalBalance, SubledgerType
from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("code", name="uq_account_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    name_ar: Mapped[str] = mapped_column(String(200))
    name_en: Mapped[str] = mapped_column(String(200))
    level: Mapped[int] = mapped_column(Integer, index=True)
    account_type: Mapped[AccountMainType] = mapped_column(Enum(AccountMainType, name="account_main_type"))
    financial_statement_type: Mapped[FinancialStatementType] = mapped_column(
        Enum(FinancialStatementType, name="financial_statement_type")
    )
    normal_balance: Mapped[NormalBalance] = mapped_column(Enum(NormalBalance, name="normal_balance_type"))
    is_postable: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_subledger: Mapped[bool] = mapped_column(Boolean, default=False)
    subledger_type: Mapped[SubledgerType] = mapped_column(Enum(SubledgerType, name="subledger_type"), default=SubledgerType.NONE)
    allow_manual_entry: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_reconciliation: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    parent: Mapped["Account | None"] = relationship(remote_side=[id])
    dimension_rules: Mapped[list["AccountDimensionRule"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class AccountDimensionRule(Base):
    __tablename__ = "account_dimension_rules"
    __table_args__ = (UniqueConstraint("account_id", "dimension_code", name="uq_account_dimension_rule"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    dimension_code: Mapped[DimensionCode] = mapped_column(Enum(DimensionCode, name="dimension_code"))
    is_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)

    account: Mapped[Account] = relationship(back_populates="dimension_rules")
