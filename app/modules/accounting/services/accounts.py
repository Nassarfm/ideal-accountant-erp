from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.common.enums import DimensionCode, SubledgerType
from app.common.exceptions import ValidationException
from app.modules.accounting.models.accounts import Account, AccountDimensionRule
from app.modules.accounting.schemas.accounts import AccountCreate, AccountRulesUpdate

POSTING_LEVEL = 4
MAX_LEVEL = 4


def _validate_account_code(code: str) -> None:
    if not code.isdigit():
        raise ValidationException("Account code must contain digits only.")


def _validate_rule_payload(rule_map: dict[DimensionCode, object]) -> None:
    for code, rule in rule_map.items():
        if code in {DimensionCode.LEGAL_ENTITY, DimensionCode.BRANCH, DimensionCode.MAIN_ACCOUNT}:
            raise ValidationException(
                f"{code.value} is managed by the posting engine and should not be added as an account dimension rule."
            )
        if rule.is_required and not rule.is_allowed:
            raise ValidationException(f"Dimension {code.value} cannot be required when it is not allowed.")


def create_account(db: Session, payload: AccountCreate) -> Account:
    _validate_account_code(payload.code)

    existing = db.scalar(select(Account).where(Account.code == payload.code))
    if existing:
        raise ValidationException(f"Account code {payload.code} already exists.")

    if payload.level < 1 or payload.level > MAX_LEVEL:
        raise ValidationException(f"Account level must be between 1 and {MAX_LEVEL}.")

    parent: Account | None = None
    if payload.level == 1:
        if payload.parent_id is not None:
            raise ValidationException("Level 1 account cannot have a parent.")
    else:
        if payload.parent_id is None:
            raise ValidationException(f"Level {payload.level} account requires a parent account.")
        parent = db.get(Account, payload.parent_id)
        if not parent:
            raise ValidationException("Parent account not found.")
        if parent.level >= MAX_LEVEL:
            raise ValidationException(f"Cannot create a child under a level {MAX_LEVEL} posting account.")
        if payload.level != parent.level + 1:
            raise ValidationException("Child account level must equal parent level + 1.")
        if parent.is_postable:
            raise ValidationException("Cannot create a child under a postable account.")
        if payload.code == parent.code or len(payload.code) <= len(parent.code):
            raise ValidationException("Child account code must be longer than parent account code.")
        if not payload.code.startswith(parent.code):
            raise ValidationException("Child account code must start with parent account code.")

    if payload.is_postable and payload.level != POSTING_LEVEL:
        raise ValidationException("Posting accounts must be level 4 in the current accounting design.")

    if not payload.is_postable and payload.level == POSTING_LEVEL:
        raise ValidationException("Level 4 accounts must be postable in the current accounting design.")

    if payload.requires_subledger and payload.subledger_type == SubledgerType.NONE:
        raise ValidationException("subledger_type is required when requires_subledger is true.")

    if not payload.requires_subledger and payload.subledger_type != SubledgerType.NONE:
        raise ValidationException("subledger_type must be NONE when requires_subledger is false.")

    rule_map = {rule.dimension_code: rule for rule in payload.dimension_rules}
    _validate_rule_payload(rule_map)

    account = Account(
        parent_id=payload.parent_id,
        code=payload.code,
        name_ar=payload.name_ar,
        name_en=payload.name_en,
        level=payload.level,
        account_type=payload.account_type,
        financial_statement_type=payload.financial_statement_type,
        normal_balance=payload.normal_balance,
        is_postable=payload.is_postable,
        requires_subledger=payload.requires_subledger,
        subledger_type=payload.subledger_type,
        allow_manual_entry=payload.allow_manual_entry,
        allow_reconciliation=payload.allow_reconciliation,
        is_active=payload.is_active,
        dimension_rules=[
            AccountDimensionRule(
                dimension_code=rule.dimension_code,
                is_allowed=rule.is_allowed,
                is_required=rule.is_required,
            )
            for rule in payload.dimension_rules
        ],
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account_rules(db: Session, account_id: int, payload: AccountRulesUpdate) -> Account:
    account = db.scalar(select(Account).options(selectinload(Account.dimension_rules)).where(Account.id == account_id))
    if not account:
        raise ValidationException("Account not found.")

    if not account.is_postable:
        raise ValidationException("Rules engine can only be configured for posting accounts.")

    if payload.requires_subledger and payload.subledger_type == SubledgerType.NONE:
        raise ValidationException("subledger_type is required when requires_subledger is true.")

    if not payload.requires_subledger and payload.subledger_type != SubledgerType.NONE:
        raise ValidationException("subledger_type must be NONE when requires_subledger is false.")

    rule_map = {rule.dimension_code: rule for rule in payload.dimension_rules}
    _validate_rule_payload(rule_map)

    account.requires_subledger = payload.requires_subledger
    account.subledger_type = payload.subledger_type
    account.allow_manual_entry = payload.allow_manual_entry
    account.allow_reconciliation = payload.allow_reconciliation
    account.is_active = payload.is_active

    account.dimension_rules.clear()
    account.dimension_rules.extend(
        [
            AccountDimensionRule(
                dimension_code=rule.dimension_code,
                is_allowed=rule.is_allowed,
                is_required=rule.is_required,
            )
            for rule in payload.dimension_rules
        ]
    )
    db.commit()
    db.refresh(account)
    return account


def list_accounts(db: Session) -> list[Account]:
    stmt = select(Account).options(selectinload(Account.dimension_rules)).order_by(Account.code)
    return list(db.scalars(stmt).unique())


def get_account_tree(db: Session) -> list[dict]:
    accounts = list_accounts(db)
    node_map: dict[int, dict] = {}
    roots: list[dict] = []

    for account in accounts:
        node_map[account.id] = {
            "id": account.id,
            "parent_id": account.parent_id,
            "code": account.code,
            "name_ar": account.name_ar,
            "name_en": account.name_en,
            "level": account.level,
            "account_type": account.account_type,
            "financial_statement_type": account.financial_statement_type,
            "normal_balance": account.normal_balance,
            "is_postable": account.is_postable,
            "requires_subledger": account.requires_subledger,
            "subledger_type": account.subledger_type,
            "allow_manual_entry": account.allow_manual_entry,
            "allow_reconciliation": account.allow_reconciliation,
            "is_active": account.is_active,
            "dimension_rules": [
                {
                    "id": rule.id,
                    "dimension_code": rule.dimension_code,
                    "is_allowed": rule.is_allowed,
                    "is_required": rule.is_required,
                }
                for rule in account.dimension_rules
            ],
            "children": [],
        }

    for account in accounts:
        node = node_map[account.id]
        if account.parent_id and account.parent_id in node_map:
            node_map[account.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


def generate_next_account_code(db: Session, parent_id: int) -> str:
    parent = db.get(Account, parent_id)
    if not parent:
        raise ValidationException("Parent account not found.")

    if parent.level >= MAX_LEVEL:
        raise ValidationException(f"Cannot generate child code under a level {MAX_LEVEL} posting account.")

    children_stmt = (
        select(Account)
        .where(Account.parent_id == parent_id)
        .order_by(Account.code)
    )
    children = list(db.scalars(children_stmt))

    parent_code = parent.code

    if not children:
        return f"{parent_code}01"

    suffix_lengths = []
    suffix_numbers = []

    for child in children:
        if not child.code.startswith(parent_code):
            continue

        suffix = child.code[len(parent_code):]
        if not suffix.isdigit():
            continue

        suffix_lengths.append(len(suffix))
        suffix_numbers.append(int(suffix))

    if not suffix_numbers:
        return f"{parent_code}01"

    suffix_width = max(suffix_lengths) if suffix_lengths else 2
    next_number = max(suffix_numbers) + 1

    return f"{parent_code}{str(next_number).zfill(suffix_width)}"