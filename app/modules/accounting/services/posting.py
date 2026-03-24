from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.modules.accounting.models.ledger import LedgerEntry
from app.modules.accounting.models.balance import AccountBalance
from app.modules.accounting.models.journal import JournalEntry

async def post_journal_entry(db: AsyncSession, journal_entry_id):
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.id == journal_entry_id)
    )
    je = result.scalar_one_or_none()

    if not je:
        raise Exception("Journal Entry not found")

    if je.status != "APPROVED":
        raise Exception("Must be APPROVED first")

    for line in je.lines:
        ledger = LedgerEntry(
            journal_entry_id=je.id,
            account_code=line.account_code,
            entry_date=je.entry_date,
            debit=line.debit,
            credit=line.credit,
            description=line.description,
        )
        db.add(ledger)

        result = await db.execute(
            select(AccountBalance).where(
                AccountBalance.account_code == line.account_code
            )
        )
        balance = result.scalar_one_or_none()

        if not balance:
            balance = AccountBalance(
                account_code=line.account_code,
                debit_total=0,
                credit_total=0,
            )
            db.add(balance)

        balance.debit_total += Decimal(line.debit or 0)
        balance.credit_total += Decimal(line.credit or 0)

    je.status = "POSTED"

    await db.commit()
