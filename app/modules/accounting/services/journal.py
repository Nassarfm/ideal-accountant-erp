from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.common.enums import DimensionCode, JournalEntryStatus, SubledgerType
from app.common.exceptions import ValidationException
from app.modules.accounting.models.accounts import Account
from app.modules.accounting.models.dimensions import (
    BusinessLine,
    CostCenter,
    Department,
    GeographicRegion,
    Project,
    ReserveDimension9,
    ReserveDimension10,
)
from app.modules.accounting.models.entities import Branch, LegalEntity
from app.modules.accounting.models.fiscal import FiscalYear
from app.modules.accounting.models.journal import JournalEntry, JournalEntryLine, LedgerEntry
from app.modules.accounting.models.subledgers import BankAccount, Customer, FixedAsset, Vendor
from app.modules.accounting.models.vouchers import VoucherType
from app.modules.accounting.schemas.journal import JournalEntryCreate
from app.modules.accounting.services.vouchers import next_document_number

DIMENSION_TO_FIELD = {
    DimensionCode.COST_CENTER: "cost_center_id",
    DimensionCode.DEPARTMENT: "department_id",
    DimensionCode.PROJECT: "project_id",
    DimensionCode.GEOGRAPHIC_REGION: "geographic_region_id",
    DimensionCode.BUSINESS_LINE: "business_line_id",
    DimensionCode.RESERVE_9: "reserve_dimension_9_id",
    DimensionCode.RESERVE_10: "reserve_dimension_10_id",
}

FIELD_TO_MODEL = {
    "cost_center_id": CostCenter,
    "department_id": Department,
    "project_id": Project,
    "geographic_region_id": GeographicRegion,
    "business_line_id": BusinessLine,
    "reserve_dimension_9_id": ReserveDimension9,
    "reserve_dimension_10_id": ReserveDimension10,
}

SUBLEDGER_MODEL_MAP = {
    SubledgerType.BANK: BankAccount,
    SubledgerType.CUSTOMER: Customer,
    SubledgerType.VENDOR: Vendor,
    SubledgerType.ASSET: FixedAsset,
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _validate_dimension_value_exists(db: Session, field_name: str, value_id: int) -> None:
    model_cls = FIELD_TO_MODEL[field_name]
    if not db.get(model_cls, value_id):
        raise ValidationException(f"Dimension value for {field_name} with id {value_id} was not found.")


def _validate_subledger_reference(db: Session, subledger_type: SubledgerType, subledger_reference: str) -> None:
    model_cls = SUBLEDGER_MODEL_MAP.get(subledger_type)
    if not model_cls:
        return
    entity = db.scalar(select(model_cls).where(model_cls.code == subledger_reference))
    if not entity:
        raise ValidationException(
            f"Subledger reference {subledger_reference} was not found for subledger type {subledger_type.value}."
        )
    if not entity.is_active:
        raise ValidationException(
            f"Subledger reference {subledger_reference} is inactive for subledger type {subledger_type.value}."
        )


def _load_journal_entry(db: Session, journal_entry_id: int) -> JournalEntry:
    stmt = (
        select(JournalEntry)
        .options(
            selectinload(JournalEntry.lines).selectinload(JournalEntryLine.journal_entry),
            selectinload(JournalEntry.ledger_entries),
        )
        .where(JournalEntry.id == journal_entry_id)
    )
    entry = db.scalar(stmt)
    if not entry:
        raise ValidationException("Journal entry not found.")
    return entry


def _validate_journal_entry_payload(db: Session, payload: JournalEntryCreate) -> tuple[FiscalYear, VoucherType]:
    if len(payload.lines) < 2:
        raise ValidationException("A journal entry must contain at least two lines.")

    fiscal_year = db.get(FiscalYear, payload.fiscal_year_id)
    if not fiscal_year:
        raise ValidationException("Fiscal year not found.")
    if fiscal_year.is_closed:
        raise ValidationException("Fiscal year is closed.")
    if not (fiscal_year.start_date <= payload.entry_date <= fiscal_year.end_date):
        raise ValidationException("Entry date is outside the selected fiscal year.")

    voucher_type = db.get(VoucherType, payload.voucher_type_id)
    if not voucher_type or not voucher_type.is_active:
        raise ValidationException("Voucher type not found or inactive.")

    total_debit = sum((line.debit_amount for line in payload.lines), Decimal("0.00"))
    total_credit = sum((line.credit_amount for line in payload.lines), Decimal("0.00"))
    if total_debit != total_credit:
        raise ValidationException("Journal entry is not balanced.")

    branch_cache: dict[int, Branch] = {}
    legal_entity_cache: dict[int, LegalEntity] = {}
    account_cache: dict[int, Account] = {}

    for line in payload.lines:
        legal_entity = legal_entity_cache.get(line.legal_entity_id) or db.get(LegalEntity, line.legal_entity_id)
        if not legal_entity:
            raise ValidationException(f"Legal entity {line.legal_entity_id} not found.")
        legal_entity_cache[line.legal_entity_id] = legal_entity

        branch = branch_cache.get(line.branch_id) or db.get(Branch, line.branch_id)
        if not branch:
            raise ValidationException(f"Branch {line.branch_id} not found.")
        branch_cache[line.branch_id] = branch
        if branch.legal_entity_id != line.legal_entity_id:
            raise ValidationException(f"Branch {line.branch_id} does not belong to legal entity {line.legal_entity_id}.")

        account = account_cache.get(line.account_id) or db.get(Account, line.account_id)
        if not account:
            raise ValidationException(f"Account {line.account_id} not found.")
        account_cache[line.account_id] = account

        if not account.is_active:
            raise ValidationException(f"Account {account.code} is inactive.")
        if not account.is_postable or account.level != 4:
            raise ValidationException(f"Account {account.code} is not a level-4 posting account.")
        if not account.allow_manual_entry:
            raise ValidationException(f"Manual entries are not allowed for account {account.code}.")

        if account.requires_subledger:
            if line.subledger_type != account.subledger_type:
                raise ValidationException(
                    f"Account {account.code} requires subledger type {account.subledger_type.value}."
                )
            if not line.subledger_reference:
                raise ValidationException(f"Account {account.code} requires a subledger reference.")
            _validate_subledger_reference(db, line.subledger_type, line.subledger_reference)
        else:
            if line.subledger_type != SubledgerType.NONE:
                raise ValidationException(f"Account {account.code} does not allow subledger_type on manual entry.")
            if line.subledger_reference:
                raise ValidationException(f"Account {account.code} does not allow subledger_reference on manual entry.")

        rule_map = {rule.dimension_code: rule for rule in account.dimension_rules}
        for dimension_code, field_name in DIMENSION_TO_FIELD.items():
            value_id = getattr(line, field_name)
            rule = rule_map.get(dimension_code)
            if rule:
                if rule.is_required and value_id is None:
                    raise ValidationException(
                        f"Account {account.code} requires dimension {dimension_code.value} on each line."
                    )
                if not rule.is_allowed and value_id is not None:
                    raise ValidationException(
                        f"Account {account.code} does not allow dimension {dimension_code.value}."
                    )
            elif value_id is not None:
                raise ValidationException(
                    f"Account {account.code} does not allow dimension {dimension_code.value}."
                )

            if value_id is not None:
                _validate_dimension_value_exists(db, field_name, value_id)

    return fiscal_year, voucher_type


def create_journal_entry(db: Session, payload: JournalEntryCreate) -> JournalEntry:
    _validate_journal_entry_payload(db, payload)
    entry_number = next_document_number(db, payload.voucher_type_id, payload.fiscal_year_id)

    entry = JournalEntry(
        entry_number=entry_number,
        voucher_type_id=payload.voucher_type_id,
        fiscal_year_id=payload.fiscal_year_id,
        entry_date=payload.entry_date,
        reference=payload.reference,
        currency_code=payload.currency_code,
        description=payload.description,
        status=JournalEntryStatus.DRAFT,
    )
    db.add(entry)
    db.flush()

    for idx, line in enumerate(payload.lines, start=1):
        db.add(
            JournalEntryLine(
                journal_entry_id=entry.id,
                line_number=idx,
                legal_entity_id=line.legal_entity_id,
                branch_id=line.branch_id,
                account_id=line.account_id,
                subledger_type=line.subledger_type,
                subledger_reference=line.subledger_reference,
                cost_center_id=line.cost_center_id,
                department_id=line.department_id,
                project_id=line.project_id,
                geographic_region_id=line.geographic_region_id,
                business_line_id=line.business_line_id,
                reserve_dimension_9_id=line.reserve_dimension_9_id,
                reserve_dimension_10_id=line.reserve_dimension_10_id,
                line_description=line.line_description,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
            )
        )

    db.commit()
    return get_journal_entry(db, entry.id)


def get_journal_entry(db: Session, journal_entry_id: int) -> JournalEntry:
    stmt = (
        select(JournalEntry)
        .options(
            selectinload(JournalEntry.lines),
            selectinload(JournalEntry.ledger_entries),
        )
        .where(JournalEntry.id == journal_entry_id)
    )
    entry = db.scalar(stmt)
    if not entry:
        raise ValidationException("Journal entry not found.")
    return entry


def list_journal_entries(db: Session) -> list[JournalEntry]:
    stmt = (
        select(JournalEntry)
        .options(selectinload(JournalEntry.lines), selectinload(JournalEntry.ledger_entries))
        .order_by(JournalEntry.id.desc())
    )
    return list(db.scalars(stmt).unique())


def approve_journal_entry(db: Session, journal_entry_id: int) -> JournalEntry:
    entry = get_journal_entry(db, journal_entry_id)
    if entry.status != JournalEntryStatus.DRAFT:
        raise ValidationException("Only draft journal entries can be approved.")
    if not entry.lines:
        raise ValidationException("Journal entry has no lines.")

    payload = JournalEntryCreate(
        voucher_type_id=entry.voucher_type_id,
        fiscal_year_id=entry.fiscal_year_id,
        entry_date=entry.entry_date,
        reference=entry.reference,
        currency_code=entry.currency_code,
        description=entry.description,
        lines=[
            {
                "legal_entity_id": line.legal_entity_id,
                "branch_id": line.branch_id,
                "account_id": line.account_id,
                "subledger_type": line.subledger_type,
                "subledger_reference": line.subledger_reference,
                "cost_center_id": line.cost_center_id,
                "department_id": line.department_id,
                "project_id": line.project_id,
                "geographic_region_id": line.geographic_region_id,
                "business_line_id": line.business_line_id,
                "reserve_dimension_9_id": line.reserve_dimension_9_id,
                "reserve_dimension_10_id": line.reserve_dimension_10_id,
                "line_description": line.line_description,
                "debit_amount": line.debit_amount,
                "credit_amount": line.credit_amount,
            }
            for line in entry.lines
        ],
    )
    _validate_journal_entry_payload(db, payload)

    entry.status = JournalEntryStatus.APPROVED
    entry.approved_at = _utcnow()
    db.commit()
    return get_journal_entry(db, journal_entry_id)


def post_journal_entry(db: Session, journal_entry_id: int) -> JournalEntry:
    entry = get_journal_entry(db, journal_entry_id)
    if entry.status != JournalEntryStatus.APPROVED:
        raise ValidationException("Only approved journal entries can be posted.")
    if entry.ledger_entries:
        raise ValidationException("Journal entry is already posted to ledger.")

    ledger_rows: list[LedgerEntry] = []
    for line in entry.lines:
        ledger_rows.append(
            LedgerEntry(
                journal_entry_id=entry.id,
                journal_entry_line_id=line.id,
                entry_number=entry.entry_number,
                entry_date=entry.entry_date,
                fiscal_year_id=entry.fiscal_year_id,
                voucher_type_id=entry.voucher_type_id,
                legal_entity_id=line.legal_entity_id,
                branch_id=line.branch_id,
                account_id=line.account_id,
                subledger_type=line.subledger_type.value if isinstance(line.subledger_type, SubledgerType) else str(line.subledger_type),
                subledger_reference=line.subledger_reference,
                cost_center_id=line.cost_center_id,
                department_id=line.department_id,
                project_id=line.project_id,
                geographic_region_id=line.geographic_region_id,
                business_line_id=line.business_line_id,
                reserve_dimension_9_id=line.reserve_dimension_9_id,
                reserve_dimension_10_id=line.reserve_dimension_10_id,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
                posted_at=_utcnow(),
            )
        )

    db.add_all(ledger_rows)
    entry.status = JournalEntryStatus.POSTED
    entry.posted_at = _utcnow()
    db.commit()
    return get_journal_entry(db, journal_entry_id)


def list_ledger_entries(db: Session) -> list[LedgerEntry]:
    stmt = select(LedgerEntry).order_by(LedgerEntry.id.desc())
    return list(db.scalars(stmt))
