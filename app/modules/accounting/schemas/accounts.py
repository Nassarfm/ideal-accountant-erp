from __future__ import annotations

from pydantic import BaseModel, Field

from app.common.enums import AccountMainType, DimensionCode, FinancialStatementType, NormalBalance, SubledgerType
from app.modules.accounting.schemas.common import ORMBaseSchema


class AccountDimensionRulePayload(BaseModel):
    dimension_code: DimensionCode
    is_allowed: bool = False
    is_required: bool = False


class AccountCreate(BaseModel):
    parent_id: int | None = None
    code: str = Field(min_length=1, max_length=50, pattern=r"^\d+$")
    name_ar: str
    name_en: str
    level: int = Field(ge=1, le=4)
    account_type: AccountMainType
    financial_statement_type: FinancialStatementType
    normal_balance: NormalBalance
    is_postable: bool = False
    requires_subledger: bool = False
    subledger_type: SubledgerType = SubledgerType.NONE
    allow_manual_entry: bool = True
    allow_reconciliation: bool = False
    is_active: bool = True
    dimension_rules: list[AccountDimensionRulePayload] = []


class AccountRulesUpdate(BaseModel):
    requires_subledger: bool
    subledger_type: SubledgerType = SubledgerType.NONE
    allow_manual_entry: bool = True
    allow_reconciliation: bool = False
    is_active: bool = True
    dimension_rules: list[AccountDimensionRulePayload] = []


class AccountDimensionRuleRead(ORMBaseSchema):
    id: int
    dimension_code: DimensionCode
    is_allowed: bool
    is_required: bool


class AccountRead(ORMBaseSchema):
    id: int
    parent_id: int | None
    code: str
    name_ar: str
    name_en: str
    level: int
    account_type: AccountMainType
    financial_statement_type: FinancialStatementType
    normal_balance: NormalBalance
    is_postable: bool
    requires_subledger: bool
    subledger_type: SubledgerType
    allow_manual_entry: bool
    allow_reconciliation: bool
    is_active: bool
    dimension_rules: list[AccountDimensionRuleRead] = []


class AccountTreeNodeRead(AccountRead):
    children: list["AccountTreeNodeRead"] = []


class AccountCodeGenerateResponse(BaseModel):
    code: str


AccountTreeNodeRead.model_rebuild()