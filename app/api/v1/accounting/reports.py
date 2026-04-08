from fastapi import APIRouter

router = APIRouter(prefix="/accounting/reports", tags=["Accounting - Reports"])


@router.get("/trial-balance")
async def trial_balance_placeholder():
    return {"message": "Trial balance endpoint placeholder - next batch will complete reports layer"}


@router.get("/ledger")
async def ledger_placeholder():
    return {"message": "Ledger endpoint placeholder - next batch will complete reports layer"}
