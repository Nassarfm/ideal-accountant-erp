from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: UUID, tenant_id: UUID) -> Account | None:
        result = await self.db.execute(
            select(Account).where(Account.id == account_id, Account.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, tenant_id: UUID) -> Account | None:
        result = await self.db.execute(
            select(Account).where(Account.code == code, Account.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, tenant_id: UUID) -> list[Account]:
        result = await self.db.execute(
            select(Account).where(Account.tenant_id == tenant_id).order_by(Account.code)
        )
        return list(result.scalars().all())

    async def create(self, account: Account) -> Account:
        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)
        return account
