from decimal import Decimal
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.accounting.models.journal import JournalEntry, JournalEntryLine
from app.modules.accounting.models.ledger import LedgerEntry


def to_decimal(value):
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


async def post_journal_entry(db: AsyncSession, journal_entry_id: int) -> JournalEntry:
    # 1️⃣ جلب القيد
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.id == journal_entry_id)
    )
    je = result.scalar_one_or_none()

    if not je:
        raise Exception("Journal Entry not found")

    if je.status != "APPROVED":
        raise Exception("Journal Entry must be APPROVED first")

    # 2️⃣ جلب السطور
    lines_result = await db.execute(
        select(JournalEntryLine).where(
            JournalEntryLine.journal_entry_id == je.id
        )
    )
    lines = lines_result.scalars().all()

    if not lines:
        raise Exception("Journal Entry has no lines")

    # 3️⃣ تحقق التوازن
    total_debit = sum(to_decimal(line.debit_amount) for line in lines)
    total_credit = sum(to_decimal(line.credit_amount) for line in lines)

    if total_debit != total_credit:
        raise Exception("Journal Entry is not balanced")

    # 4️⃣ إنشاء Ledger Entries
    for line in lines:
        ledger = LedgerEntry(
            journal_entry_id=je.id,
            journal_entry_line_id=line.id,
            entry_date=je.entry_date,
            description=line.line_description,

            legal_entity_id=je.legal_entity_id,
            branch_id=je.branch_id,

            account_id=line.account_id,

            debit=to_decimal(line.debit_amount),
            credit=to_decimal(line.credit_amount),
        )

        db.add(ledger)

    # 5️⃣ تحديث حالة القيد
    je.status = "POSTED"

    if hasattr(je, "posted_at"):
        je.posted_at = datetime.utcnow()

    # 6️⃣ حفظ
    await db.commit()
    await db.refresh(je)

    return je