from __future__ import annotations

import uuid

from app.models.account import Account
from app.repositories.accounting.account_repository import AccountRepository
from app.schemas.accounting.account import AccountCreate


class AccountService:
    def __init__(self, db, tenant_id):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = AccountRepository(db)

    async def list_accounts(self):
        return await self.repo.list_all(self.tenant_id)

    async def create_account(self, payload: AccountCreate) -> Account:
        existing = await self.repo.get_by_code(payload.code, self.tenant_id)
        if existing:
            raise ValueError("Account code already exists")

        account = Account(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            code=payload.code,
            name_ar=payload.name_ar,
            name_en=payload.name_en,
            account_type=payload.account_type,
            account_nature=payload.account_nature,
            level=payload.level,
            parent_id=payload.parent_id,
            is_postable=payload.is_postable,
            is_active=payload.is_active,
        )
        return await self.repo.create(account)
