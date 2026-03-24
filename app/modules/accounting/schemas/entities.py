from pydantic import BaseModel

from app.modules.accounting.schemas.common import ORMBaseSchema


class LegalEntityCreate(BaseModel):
    code: str
    name: str
    is_active: bool = True


class LegalEntityRead(ORMBaseSchema):
    id: int
    code: str
    name: str
    is_active: bool


class BranchCreate(BaseModel):
    legal_entity_id: int
    code: str
    name: str
    is_active: bool = True


class BranchRead(ORMBaseSchema):
    id: int
    legal_entity_id: int
    code: str
    name: str
    is_active: bool
