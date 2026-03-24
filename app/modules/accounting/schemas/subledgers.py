from __future__ import annotations

from pydantic import BaseModel, Field

from app.modules.accounting.schemas.common import ORMBaseSchema


class SubledgerCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    is_active: bool = True


class SubledgerRead(ORMBaseSchema):
    id: int
    code: str
    name: str
    is_active: bool
