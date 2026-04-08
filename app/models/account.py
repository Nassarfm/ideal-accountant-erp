from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.accounting_enums import AccountNature, AccountType


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_accounts_tenant_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    account_nature: Mapped[str] = mapped_column(String(20), nullable=False)

    level: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    is_postable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    parent: Mapped[Optional["Account"]] = relationship(
        "Account",
        remote_side="Account.id",
        back_populates="children",
    )
    children: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="parent",
        cascade="save-update",
    )

    journal_lines: Mapped[list["JournalEntryLine"]] = relationship(
        "JournalEntryLine",
        back_populates="account",
    )

    def __repr__(self) -> str:
        return f"<Account code={self.code} name_ar={self.name_ar}>"

    @property
    def account_type_enum(self) -> AccountType:
        return AccountType(self.account_type)

    @property
    def account_nature_enum(self) -> AccountNature:
        return AccountNature(self.account_nature)
