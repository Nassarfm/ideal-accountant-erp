from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.journal_entry import JournalEntry


class JournalEntryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, je_id: UUID, tenant_id: UUID) -> JournalEntry | None:
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(JournalEntry.id == je_id, JournalEntry.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, tenant_id: UUID) -> list[JournalEntry]:
        result = await self.db.execute(
            select(JournalEntry)
            .where(JournalEntry.tenant_id == tenant_id)
            .order_by(JournalEntry.entry_date.desc(), JournalEntry.entry_no.desc())
        )
        return list(result.scalars().all())

    async def create(self, journal_entry: JournalEntry) -> JournalEntry:
        self.db.add(journal_entry)
        await self.db.flush()
        await self.db.refresh(journal_entry)
        return journal_entry
