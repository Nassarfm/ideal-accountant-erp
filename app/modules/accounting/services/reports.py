from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.accounting.models.ledger import LedgerEntry
from app.modules.accounting.models.balance import AccountBalance

async def get_ledger_for_account(db: AsyncSession, account_code: str):
    result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.account_code == account_code).order_by(LedgerEntry.entry_date.asc(), LedgerEntry.id.asc())
    )
    return list(result.scalars().all())

async def get_trial_balance(db: AsyncSession, fiscal_year_id: int):
    result = await db.execute(
        select(AccountBalance).where(AccountBalance.fiscal_year_id == fiscal_year_id).order_by(AccountBalance.account_code.asc())
    )
    lines = list(result.scalars().all())
    total_debit = sum((Decimal(str(line.debit_total)) for line in lines), Decimal("0"))
    total_credit = sum((Decimal(str(line.credit_total)) for line in lines), Decimal("0"))
    return {
        "fiscal_year_id": fiscal_year_id,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "is_balanced": total_debit == total_credit,
        "lines": lines,
    }
