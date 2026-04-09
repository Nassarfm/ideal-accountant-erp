from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.modules.accounting.models.accounts import Account
from app.modules.accounting.models.dimensions import (
    BusinessLine,
    CostCenter,
    Department,
    DimensionDefinition,
    GeographicRegion,
    Project,
    ReserveDimension9,
    ReserveDimension10,
)
from app.modules.accounting.models.entities import Branch, LegalEntity
from app.modules.accounting.models.fiscal import FiscalYear
from app.modules.accounting.models.journal import JournalEntry
from app.modules.accounting.models.ledger import LedgerEntry
from app.modules.accounting.models.vouchers import DocumentSequence, VoucherType
from app.modules.accounting.schemas.accounts import (
    AccountCodeGenerateResponse,
    AccountCreate,
    AccountRead,
    AccountRulesUpdate,
    AccountTreeNodeRead,
    AccountUpdate,
)
from app.modules.accounting.schemas.dimensions import DimensionDefinitionRead, DimensionValueCreate, DimensionValueRead
from app.modules.accounting.schemas.entities import BranchCreate, BranchRead, LegalEntityCreate, LegalEntityRead
from app.modules.accounting.schemas.fiscal import FiscalYearCreate, FiscalYearRead
from app.modules.accounting.schemas.journal import JournalEntryCreate, JournalEntryRead, LedgerEntryRead
from app.modules.accounting.schemas.subledgers import SubledgerCreate, SubledgerRead
from app.modules.accounting.schemas.vouchers import DocumentSequenceRead, VoucherTypeCreate, VoucherTypeRead
from app.modules.accounting.services.accounts import (
    create_account,
    generate_next_account_code,
    get_account_tree,
    list_accounts,
    update_account,
    update_account_rules,
)
from app.modules.accounting.services.fiscal import create_fiscal_year
from app.modules.accounting.services.journal import (
    approve_journal_entry,
    create_journal_entry,
    get_journal_entry,
    list_journal_entries,
    list_ledger_entries,
    post_journal_entry,
)
from app.modules.accounting.services.master_data import create_simple_entity, list_dimension_definitions
from app.modules.accounting.services.subledgers import SUBLEDGER_ENDPOINT_MAP, create_subledger_entity, list_subledger_entities
from app.modules.accounting.services.vouchers import create_voucher_type, list_document_sequences, list_voucher_types

router = APIRouter(prefix="/accounting", tags=["Accounting Core"])

DIMENSION_ENDPOINT_MAP = {
    "cost-centers": CostCenter,
    "departments": Department,
    "projects": Project,
    "geographic-regions": GeographicRegion,
    "business-lines": BusinessLine,
    "reserve-dimension-9": ReserveDimension9,
    "reserve-dimension-10": ReserveDimension10,
}


@router.get("/dimension-definitions", response_model=list[DimensionDefinitionRead])
def get_dimension_definitions(db: Session = Depends(get_db)) -> list[DimensionDefinition]:
    return list_dimension_definitions(db)


@router.post("/legal-entities", response_model=LegalEntityRead, status_code=201)
def create_legal_entity_endpoint(payload: LegalEntityCreate, db: Session = Depends(get_db)) -> LegalEntity:
    return create_simple_entity(db, LegalEntity, code=payload.code, name=payload.name, is_active=payload.is_active)


@router.get("/legal-entities", response_model=list[LegalEntityRead])
def list_legal_entities_endpoint(db: Session = Depends(get_db)) -> list[LegalEntity]:
    return list(db.scalars(select(LegalEntity).order_by(LegalEntity.code)))


@router.post("/branches", response_model=BranchRead, status_code=201)
def create_branch_endpoint(payload: BranchCreate, db: Session = Depends(get_db)) -> Branch:
    return create_simple_entity(
        db,
        Branch,
        code=payload.code,
        name=payload.name,
        is_active=payload.is_active,
        legal_entity_id=payload.legal_entity_id,
    )


@router.get("/branches", response_model=list[BranchRead])
def list_branches_endpoint(db: Session = Depends(get_db)) -> list[Branch]:
    return list(db.scalars(select(Branch).order_by(Branch.code)))


for path, model in DIMENSION_ENDPOINT_MAP.items():
    def _create_create_endpoint(model_cls):
        def endpoint(payload: DimensionValueCreate, db: Session = Depends(get_db)):
            return create_simple_entity(db, model_cls, code=payload.code, name=payload.name, is_active=payload.is_active)
        return endpoint

    def _create_list_endpoint(model_cls):
        def endpoint(db: Session = Depends(get_db)):
            return list(db.scalars(select(model_cls).order_by(model_cls.code)))
        return endpoint

    router.post(f"/{path}", response_model=DimensionValueRead, status_code=201)(_create_create_endpoint(model))
    router.get(f"/{path}", response_model=list[DimensionValueRead])(_create_list_endpoint(model))


for path, model in SUBLEDGER_ENDPOINT_MAP.items():
    def _create_create_endpoint(model_cls):
        def endpoint(payload: SubledgerCreate, db: Session = Depends(get_db)):
            return create_subledger_entity(db, model_cls, code=payload.code, name=payload.name, is_active=payload.is_active)
        return endpoint

    def _create_list_endpoint(model_cls):
        def endpoint(db: Session = Depends(get_db)):
            return list_subledger_entities(db, model_cls)
        return endpoint

    router.post(f"/{path}", response_model=SubledgerRead, status_code=201)(_create_create_endpoint(model))
    router.get(f"/{path}", response_model=list[SubledgerRead])(_create_list_endpoint(model))


@router.post("/voucher-types", response_model=VoucherTypeRead, status_code=201)
def create_voucher_type_endpoint(payload: VoucherTypeCreate, db: Session = Depends(get_db)) -> VoucherType:
    return create_voucher_type(db, payload)


@router.get("/voucher-types", response_model=list[VoucherTypeRead])
def list_voucher_types_endpoint(db: Session = Depends(get_db)) -> list[VoucherType]:
    return list_voucher_types(db)


@router.get("/document-sequences", response_model=list[DocumentSequenceRead])
def list_document_sequences_endpoint(db: Session = Depends(get_db)) -> list[DocumentSequence]:
    return list_document_sequences(db)


@router.post("/accounts", response_model=AccountRead, status_code=201)
def create_account_endpoint(payload: AccountCreate, db: Session = Depends(get_db)):
    return create_account(db, payload)


@router.get("/accounts", response_model=list[AccountRead])
def list_accounts_endpoint(db: Session = Depends(get_db)):
    return list_accounts(db)


@router.get("/accounts/tree", response_model=list[AccountTreeNodeRead])
def get_account_tree_endpoint(db: Session = Depends(get_db)):
    return get_account_tree(db)


@router.get("/accounts/generate-code", response_model=AccountCodeGenerateResponse)
def generate_account_code_endpoint(parent_id: int, db: Session = Depends(get_db)):
    code = generate_next_account_code(db, parent_id)
    return AccountCodeGenerateResponse(code=code)


@router.put("/accounts/{account_id}", response_model=AccountRead)
def update_account_endpoint(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    return update_account(db, account_id, payload)


@router.put("/accounts/{account_id}/rules", response_model=AccountRead)
def update_account_rules_endpoint(account_id: int, payload: AccountRulesUpdate, db: Session = Depends(get_db)):
    return update_account_rules(db, account_id, payload)


@router.post("/fiscal-years", response_model=FiscalYearRead, status_code=201)
def create_fiscal_year_endpoint(payload: FiscalYearCreate, db: Session = Depends(get_db)):
    return create_fiscal_year(db, payload)


@router.get("/fiscal-years", response_model=list[FiscalYearRead])
def list_fiscal_years(db: Session = Depends(get_db)) -> list[FiscalYear]:
    return list(db.scalars(select(FiscalYear).order_by(FiscalYear.start_date.desc())))


@router.post("/journal-entries", response_model=JournalEntryRead, status_code=201)
def create_journal_entry_endpoint(payload: JournalEntryCreate, db: Session = Depends(get_db)):
    return create_journal_entry(db, payload)


@router.get("/journal-entries", response_model=list[JournalEntryRead])
def list_journal_entries_endpoint(db: Session = Depends(get_db)) -> list[JournalEntry]:
    return list_journal_entries(db)


@router.get("/journal-entries/{journal_entry_id}", response_model=JournalEntryRead)
def get_journal_entry_endpoint(journal_entry_id: int, db: Session = Depends(get_db)) -> JournalEntry:
    return get_journal_entry(db, journal_entry_id)


@router.post("/journal-entries/{journal_entry_id}/approve", response_model=JournalEntryRead)
def approve_journal_entry_endpoint(journal_entry_id: int, db: Session = Depends(get_db)) -> JournalEntry:
    return approve_journal_entry(db, journal_entry_id)


@router.post("/journal-entries/{journal_entry_id}/post", response_model=JournalEntryRead)
def post_journal_entry_endpoint(journal_entry_id: int, db: Session = Depends(get_db)) -> JournalEntry:
    return post_journal_entry(db, journal_entry_id)


@router.get("/ledger-entries", response_model=list[LedgerEntryRead])
def list_ledger_entries_endpoint(db: Session = Depends(get_db)) -> list[LedgerEntry]:
    return list_ledger_entries(db)