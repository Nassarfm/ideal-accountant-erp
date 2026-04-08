from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fiscal_period import FiscalPeriod
from app.models.fiscal_lock import FiscalLock


class FiscalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_periods(self, tenant_id):
        result = await self.db.execute(
            select(FiscalPeriod)
            .where(FiscalPeriod.tenant_id == tenant_id)
            .order_by(FiscalPeriod.fiscal_year.desc(), FiscalPeriod.period_no.asc())
        )
        return list(result.scalars().all())

    async def create_period(self, period: FiscalPeriod) -> FiscalPeriod:
        self.db.add(period)
        await self.db.flush()
        await self.db.refresh(period)
        return period

    async def create_lock(self, lock: FiscalLock) -> FiscalLock:
        self.db.add(lock)
        await self.db.flush()
        await self.db.refresh(lock)
        return lock
