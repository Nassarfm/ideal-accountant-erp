from pydantic import BaseModel

from app.modules.accounting.schemas.common import ORMBaseSchema


class DimensionDefinitionRead(ORMBaseSchema):
    id: int
    sort_order: int
    code: str
    name_en: str
    name_ar: str
    is_reserved: bool
    is_active: bool


class SimpleDimensionCreate(BaseModel):
    code: str
    name: str
    is_active: bool = True


class SimpleDimensionRead(ORMBaseSchema):
    id: int
    code: str
    name: str
    is_active: bool


# Backward-compatible aliases used by the router
class DimensionValueCreate(SimpleDimensionCreate):
    pass


class DimensionValueRead(SimpleDimensionRead):
    pass
