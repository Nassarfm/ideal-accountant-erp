from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.exceptions import ValidationException
from app.modules.accounting.models.fiscal import FiscalYear
from app.modules.accounting.models.vouchers import DocumentSequence, VoucherType
from app.modules.accounting.schemas.vouchers import VoucherTypeCreate

DEFAULT_VOUCHER_TYPES = [
    ("JV", "Journal Voucher", "General journal voucher"),
    ("PV", "Payment Voucher", "Payment voucher"),
    ("RV", "Receipt Voucher", "Receipt voucher"),
    ("SV", "Sales Voucher", "Sales voucher"),
    ("PRV", "Purchase Voucher", "Purchase voucher"),
    ("PRJ", "Payroll Entry", "Payroll journal entry"),
    ("ACR", "Accrual Entry", "Accrual journal entry"),
    ("EXP", "Expense Entry", "Expense journal entry"),
    ("PET", "Petty Cash Entry", "Petty cash expense entry"),
    ("REC", "Recurring Entry", "Recurring journal entry template base"),
]


def list_voucher_types(db: Session) -> list[VoucherType]:
    return list(db.scalars(select(VoucherType).order_by(VoucherType.code)))


def create_voucher_type(db: Session, payload: VoucherTypeCreate) -> VoucherType:
    code = payload.code.strip().upper()
    if not code.isalnum():
        raise ValidationException("Voucher type code must contain letters and numbers only.")
    existing = db.scalar(select(VoucherType).where(VoucherType.code == code))
    if existing:
        raise ValidationException(f"Voucher type code {code} already exists.")

    obj = VoucherType(
        code=code,
        name=payload.name.strip(),
        description=payload.description,
        is_system=False,
        is_active=payload.is_active,
        reset_by_fiscal_year=payload.reset_by_fiscal_year,
        padding=payload.padding,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_document_sequences(db: Session) -> list[DocumentSequence]:
    return list(db.scalars(select(DocumentSequence).order_by(DocumentSequence.fiscal_year_id, DocumentSequence.voucher_type_id)))


def next_document_number(db: Session, voucher_type_id: int, fiscal_year_id: int) -> str:
    voucher_type = db.get(VoucherType, voucher_type_id)
    if not voucher_type or not voucher_type.is_active:
        raise ValidationException("Voucher type not found or inactive.")

    fiscal_year = db.get(FiscalYear, fiscal_year_id)
    if not fiscal_year:
        raise ValidationException("Fiscal year not found.")

    sequence = db.scalar(
        select(DocumentSequence).where(
            DocumentSequence.voucher_type_id == voucher_type_id,
            DocumentSequence.fiscal_year_id == fiscal_year_id,
        )
    )
    if not sequence:
        sequence = DocumentSequence(voucher_type_id=voucher_type_id, fiscal_year_id=fiscal_year_id, current_number=0)
        db.add(sequence)
        db.flush()

    sequence.current_number += 1
    year_text = fiscal_year.name
    return f"{voucher_type.code}-{year_text}-{sequence.current_number:0{voucher_type.padding}d}"
