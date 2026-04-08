from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.db.session import get_db
except ImportError:
    try:
        from app.db.database import get_db
    except ImportError:
        from app.api.deps import get_db

from app.modules.accounting.schemas.gl import GLResponse
from app.modules.accounting.services.gl_service import GLService

router = APIRouter(prefix="/accounting/gl", tags=["General Ledger"])

# ✅ Local test mode
# مؤقتًا نثبت legal_entity_id = 1 حتى نختبر GL بسرعة
TEST_LEGAL_ENTITY_ID = "1"


@router.get("", response_model=GLResponse)
async def get_gl(
    account_code: str = Query(...),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    date_from_parsed = date.fromisoformat(date_from) if date_from else None
    date_to_parsed = date.fromisoformat(date_to) if date_to else None

    service = GLService(db, TEST_LEGAL_ENTITY_ID)

    return await service.get_general_ledger(
        account_code=account_code,
        date_from=date_from_parsed,
        date_to=date_to_parsed,
    )