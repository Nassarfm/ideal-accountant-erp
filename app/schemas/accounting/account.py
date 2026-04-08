from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    code: str
    name_ar: str
    name_en: Optional[str] = None
    account_type: str
    account_nature: str
    level: int
    parent_id: Optional[UUID] = None
    is_postable: bool = True
    is_active: bool = True


class AccountUpdate(BaseModel):
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    account_type: Optional[str] = None
    account_nature: Optional[str] = None
    level: Optional[int] = None
    parent_id: Optional[UUID] = None
    is_postable: Optional[bool] = None
    is_active: Optional[bool] = None


class AccountRead(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name_ar: str
    name_en: Optional[str] = None
    account_type: str
    account_nature: str
    level: int
    parent_id: Optional[UUID] = None
    is_postable: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
