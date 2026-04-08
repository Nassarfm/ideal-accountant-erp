from decimal import Decimal

from sqlalchemy import select

from app.modules.accounting.models.ledger import LedgerEntry


class LedgerRepository:
    def __init__(self, db):
        self.db = db

    async def get_account_entries(
        self,
        legal_entity_id: str,
        account_code: str,
        date_from=None,
        date_to=None,
    ):
        query = select(LedgerEntry).where(
            LedgerEntry.account_code == account_code,
            LedgerEntry.legal_entity_id == legal_entity_id,
        )

        if date_from:
            query = query.where(LedgerEntry.entry_date >= date_from)

        if date_to:
            query = query.where(LedgerEntry.entry_date <= date_to)

        query = query.order_by(LedgerEntry.entry_date, LedgerEntry.id)

        # ✅ db عندك Sync Session
        result = self.db.execute(query)
        return result.scalars().all()

    async def get_opening_balance(
        self,
        legal_entity_id: str,
        account_code: str,
        date_from,
    ):
        query = select(
            LedgerEntry.debit,
            LedgerEntry.credit,
        ).where(
            LedgerEntry.account_code == account_code,
            LedgerEntry.legal_entity_id == legal_entity_id,
            LedgerEntry.entry_date < date_from,
        )

        # ✅ db عندك Sync Session
        result = self.db.execute(query)
        rows = result.all()

        opening = sum((Decimal(r.debit) - Decimal(r.credit)) for r in rows)
        return opening or Decimal("0")