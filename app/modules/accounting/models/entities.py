from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LegalEntity(Base):
    __tablename__ = "legal_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    branches: Mapped[list["Branch"]] = relationship(back_populates="legal_entity")


class Branch(Base):
    __tablename__ = "branches"
    __table_args__ = (UniqueConstraint("legal_entity_id", "code", name="uq_branch_legal_entity_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legal_entity_id: Mapped[int] = mapped_column(ForeignKey("legal_entities.id", ondelete="RESTRICT"), index=True)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    legal_entity: Mapped[LegalEntity] = relationship(back_populates="branches")
