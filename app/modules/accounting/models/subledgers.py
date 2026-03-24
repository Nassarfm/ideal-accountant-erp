from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class _SubledgerBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class BankAccount(_SubledgerBase):
    __tablename__ = "bank_accounts"
    __table_args__ = (UniqueConstraint("code", name="uq_bank_account_code"),)


class Customer(_SubledgerBase):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("code", name="uq_customer_code"),)


class Vendor(_SubledgerBase):
    __tablename__ = "vendors"
    __table_args__ = (UniqueConstraint("code", name="uq_vendor_code"),)


class FixedAsset(_SubledgerBase):
    __tablename__ = "fixed_assets"
    __table_args__ = (UniqueConstraint("code", name="uq_fixed_asset_code"),)
