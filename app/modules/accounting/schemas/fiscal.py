from datetime import date

from pydantic import BaseModel

from app.modules.accounting.schemas.common import ORMBaseSchema


class FiscalYearCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_active: bool = True


class FiscalYearRead(ORMBaseSchema):
    id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool
    is_closed: bool
