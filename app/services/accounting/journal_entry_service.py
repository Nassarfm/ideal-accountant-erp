from __future__ import annotations

import uuid

from app.models.journal_entry import JournalEntry
from app.models.journal_entry_line import JournalEntryLine
from app.repositories.accounting.journal_entry_repository import JournalEntryRepository
from app.schemas.accounting.journal_entry import JournalEntryCreate


class JournalEntryService:
    def __init__(self, db, tenant_id):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = JournalEntryRepository(db)

    async def list_journal_entries(self):
        return await self.repo.list_all(self.tenant_id)

    async def create_journal_entry(self, payload: JournalEntryCreate) -> JournalEntry:
        total_debit = sum(line.debit for line in payload.lines)
        total_credit = sum(line.credit for line in payload.lines)

        if round(total_debit, 2) != round(total_credit, 2):
            raise ValueError("Journal entry is not balanced")

        journal_entry = JournalEntry(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            entry_no="TEMP-000001",
            entry_date=payload.entry_date,
            description=payload.description,
            reference=payload.reference,
            je_type=payload.je_type,
            status="draft",
            total_debit=total_debit,
            total_credit=total_credit,
        )

        journal_entry.lines = [
            JournalEntryLine(
                id=uuid.uuid4(),
                tenant_id=self.tenant_id,
                line_no=index + 1,
                account_id=line.account_id,
                description=line.description,
                debit=line.debit,
                credit=line.credit,
            )
            for index, line in enumerate(payload.lines)
        ]

        return await self.repo.create(journal_entry)
