from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.exceptions import ValidationException
from app.modules.accounting.models.accounts import Account
from app.modules.accounting.models.ledger import LedgerEntry
from app.modules.accounting.schemas.reports import (
    LedgerEntryRead,
    TrialBalanceItem,
    TrialBalanceResponse,
)


def get_ledger_for_account(db: Session, account_code: str) -> list[LedgerEntry]:
    account = db.scalar(select(Account).where(Account.code == account_code))
    if not account:
        raise ValidationException(f"Account with code {account_code} not found.")

    stmt = (
        select(LedgerEntry)
        .where(LedgerEntry.account_id == account.id)
        .order_by(LedgerEntry.entry_date.asc(), LedgerEntry.id.asc())
    )
    return list(db.scalars(stmt).all())


def get_trial_balance(db: Session, fiscal_year_id: int) -> TrialBalanceResponse:
    stmt = (
        select(
            Account.id.label("account_id"),
            Account.code.label("account_code"),
            Account.name_ar.label("account_name_ar"),
            Account.name_en.label("account_name_en"),
            func.coalesce(func.sum(LedgerEntry.debit_amount), 0).label("total_debit"),
            func.coalesce(func.sum(LedgerEntry.credit_amount), 0).label("total_credit"),
        )
        .join(LedgerEntry, LedgerEntry.account_id == Account.id)
        .where(LedgerEntry.fiscal_year_id == fiscal_year_id)
        .group_by(Account.id, Account.code, Account.name_ar, Account.name_en)
        .order_by(Account.code.asc())
    )

    result = db.execute(stmt)
    rows = result.all()

    items: list[TrialBalanceItem] = []
    grand_debit = Decimal("0.00")
    grand_credit = Decimal("0.00")

    for row in rows:
        total_debit = Decimal(row.total_debit or 0)
        total_credit = Decimal(row.total_credit or 0)
        balance = total_debit - total_credit

        items.append(
            TrialBalanceItem(
                account_id=row.account_id,
                account_code=row.account_code,
                account_name_ar=row.account_name_ar,
                account_name_en=row.account_name_en,
                total_debit=total_debit,
                total_credit=total_credit,
                balance=balance,
            )
        )

        grand_debit += total_debit
        grand_credit += total_credit

    return TrialBalanceResponse(
        fiscal_year_id=fiscal_year_id,
        items=items,
        total_debit=grand_debit,
        total_credit=grand_credit,
        is_balanced=(grand_debit == grand_credit),
    )