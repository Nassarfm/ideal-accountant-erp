from pydantic import BaseModel, Field

from app.modules.accounting.schemas.common import ORMBaseSchema


class VoucherTypeCreate(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    is_active: bool = True
    reset_by_fiscal_year: bool = True
    padding: int = Field(default=5, ge=3, le=10)


class VoucherTypeRead(ORMBaseSchema):
    id: int
    code: str
    name: str
    description: str | None
    is_system: bool
    is_active: bool
    reset_by_fiscal_year: bool
    padding: int


class DocumentSequenceRead(ORMBaseSchema):
    id: int
    voucher_type_id: int
    fiscal_year_id: int
    current_number: int
