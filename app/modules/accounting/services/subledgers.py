from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.exceptions import ValidationException
from app.modules.accounting.models.subledgers import BankAccount, Customer, FixedAsset, Vendor

SUBLEDGER_ENDPOINT_MAP = {
    "banks": BankAccount,
    "customers": Customer,
    "vendors": Vendor,
    "fixed-assets": FixedAsset,
}


def create_subledger_entity(db: Session, model_cls, *, code: str, name: str, is_active: bool = True):
    existing = db.scalar(select(model_cls).where(model_cls.code == code))
    if existing:
        raise ValidationException(f"{model_cls.__name__} code {code} already exists.")

    obj = model_cls(code=code, name=name, is_active=is_active)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_subledger_entities(db: Session, model_cls):
    return list(db.scalars(select(model_cls).order_by(model_cls.code)))
