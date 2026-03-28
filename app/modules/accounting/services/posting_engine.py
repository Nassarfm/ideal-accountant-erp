from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.accounting.models.journal import JournalEntry, JournalEntryLine
from app.modules.accounting.models.ledger import LedgerEntry
from app.modules.accounting.models.balance import AccountBalance
from app.common.exceptions import ValidationError

def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))

async def post_journal_entry(db: AsyncSession, journal_entry_id: int) -> JournalEntry:
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == journal_entry_id))
    journal_entry = result.scalar_one_or_none()
    if not journal_entry:
        raise ValidationError("Journal entry not found.")
    if journal_entry.status != "APPROVED":
        raise ValidationError("Only APPROVED journal entries can be posted.")

    lines_result = await db.execute(select(JournalEntryLine).where(JournalEntryLine.journal_entry_id == journal_entry.id))
    lines = list(lines_result.scalars().all())
    if not lines:
        raise ValidationError("Journal entry has no lines.")

    total_debit = sum((_to_decimal(line.debit) for line in lines), Decimal("0"))
    total_credit = sum((_to_decimal(line.credit) for line in lines), Decimal("0"))
    if total_debit != total_credit:
        raise ValidationError("Journal entry is not balanced.")

    for line in lines:
        ledger_entry = LedgerEntry(
            journal_entry_id=journal_entry.id,
            journal_entry_line_id=line.id,
            entry_number=getattr(journal_entry, "entry_number", None) or str(journal_entry.id),
            entry_date=journal_entry.entry_date,
            fiscal_year_id=journal_entry.fiscal_year_id,
            voucher_type_id=getattr(journal_entry, "voucher_type_id", None),
            legal_entity_id=journal_entry.legal_entity_id,
            branch_id=journal_entry.branch_id,
            account_id=line.account_id,
            subledger_type=getattr(line, "subledger_type", None) or "NONE",
            subledger_reference=getattr(line, "subledger_reference", None),
            cost_center_id=getattr(line, "cost_center_id", None),
            department_id=getattr(line, "department_id", None),
            project_id=getattr(line, "project_id", None),
            geographic_region_id=getattr(line, "geographic_region_id", None),
            business_line_id=getattr(line, "business_line_id", None),
            reserve_dimension_9_id=getattr(line, "reserve_dimension_9_id", None),
            reserve_dimension_10_id=getattr(line, "reserve_dimension_10_id", None),
            debit_amount=_to_decimal(getattr(line, "debit", 0)),
            credit_amount=_to_decimal(getattr(line, "credit", 0)),
        )
        db.add(ledger_entry)

        bal_result = await db.execute(
            select(AccountBalance).where(
                AccountBalance.account_id == line.account_id,
                AccountBalance.fiscal_year_id == journal_entry.fiscal_year_id,
            )
        )
        balance = bal_result.scalar_one_or_none()
        if not balance:
            balance = AccountBalance(
                account_id=line.account_id,
                fiscal_year_id=journal_entry.fiscal_year_id,
                account_code=getattr(line.account, "code", ""),
                account_name=getattr(line.account, "name", ""),
                debit_total=Decimal("0"),
                credit_total=Decimal("0"),
                closing_balance=Decimal("0"),
            )
            db.add(balance)

        balance.debit_total = _to_decimal(balance.debit_total) + _to_decimal(getattr(line, "debit", 0))
        balance.credit_total = _to_decimal(balance.credit_total) + _to_decimal(getattr(line, "credit", 0))
        balance.closing_balance = _to_decimal(balance.debit_total) - _to_decimal(balance.credit_total)

    journal_entry.status = "POSTED"
    if hasattr(journal_entry, "posted_at"):
        journal_entry.posted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(journal_entry)
    return journal_entry
