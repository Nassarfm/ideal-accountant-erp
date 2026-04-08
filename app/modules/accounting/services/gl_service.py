from decimal import Decimal

from app.modules.accounting.repositories.ledger_repository import LedgerRepository
from app.modules.accounting.schemas.gl import GLResponse, GLRow


class GLService:
    def __init__(self, db, legal_entity_id: str):
        self.repo = LedgerRepository(db)
        self.legal_entity_id = legal_entity_id

    async def get_general_ledger(
        self,
        account_code: str,
        date_from=None,
        date_to=None,
    ) -> GLResponse:
        opening_balance = Decimal("0")

        if date_from:
            opening_balance = await self.repo.get_opening_balance(
                self.legal_entity_id,
                account_code,
                date_from,
            )

        entries = await self.repo.get_account_entries(
            self.legal_entity_id,
            account_code,
            date_from,
            date_to,
        )

        rows = []
        running_balance = opening_balance

        for ledger_entry in entries:
            debit = Decimal(ledger_entry.debit or 0)
            credit = Decimal(ledger_entry.credit or 0)
            running_balance += (debit - credit)

            rows.append(
                GLRow(
                    entry_date=ledger_entry.entry_date,
                    reference=ledger_entry.reference,
                    description=ledger_entry.description,
                    debit=debit,
                    credit=credit,
                    balance=running_balance,
                )
            )

        return GLResponse(
            account_code=account_code,
            account_name=None,
            opening_balance=opening_balance,
            closing_balance=running_balance,
            rows=rows,
        )