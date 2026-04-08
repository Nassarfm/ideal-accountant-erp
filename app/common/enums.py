from enum import Enum


class FinancialStatementType(str, Enum):
    BALANCE_SHEET = "BS"
    PROFIT_LOSS = "PL"


class AccountMainType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class NormalBalance(str, Enum):
    DEBIT = "DR"
    CREDIT = "CR"


class SubledgerType(str, Enum):
    NONE = "NONE"

    # Legacy / existing system value
    ASSET = "ASSET"

    # Core
    BANK = "BANK"
    CUSTOMER = "CUSTOMER"
    VENDOR = "VENDOR"
    EMPLOYEE = "EMPLOYEE"
    SHAREHOLDER = "SHAREHOLDER"
    RELATED_PARTY = "RELATED_PARTY"

    # Cash / Treasury
    CASH_CUSTODIAN = "CASH_CUSTODIAN"
    PETTY_CASH_HOLDER = "PETTY_CASH_HOLDER"
    LOAN_ACCOUNT = "LOAN_ACCOUNT"

    # Assets
    FIXED_ASSET = "FIXED_ASSET"
    INTANGIBLE_ASSET = "INTANGIBLE_ASSET"

    # Inventory & Products
    INVENTORY_CATEGORY = "INVENTORY_CATEGORY"
    PRODUCT_SERVICE = "PRODUCT_SERVICE"

    # Contracts & Documents
    RENT_CONTRACT = "RENT_CONTRACT"
    INSURANCE_POLICY = "INSURANCE_POLICY"
    LETTER_OF_CREDIT = "LETTER_OF_CREDIT"
    LETTER_OF_GUARANTEE = "LETTER_OF_GUARANTEE"

    # Operations
    BRANCH = "BRANCH"
    PROJECT = "PROJECT"
    SERVICE_PROVIDER = "SERVICE_PROVIDER"
    UTILITY_ACCOUNT = "UTILITY_ACCOUNT"

    # Compliance / Tax
    VAT_CODE = "VAT_CODE"


class JournalEntryStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    POSTED = "POSTED"
    VOID = "VOID"


class DimensionCode(str, Enum):
    LEGAL_ENTITY = "LEGAL_ENTITY"
    BRANCH = "BRANCH"
    MAIN_ACCOUNT = "MAIN_ACCOUNT"
    COST_CENTER = "COST_CENTER"
    DEPARTMENT = "DEPARTMENT"
    PROJECT = "PROJECT"
    GEOGRAPHIC_REGION = "GEOGRAPHIC_REGION"
    BUSINESS_LINE = "BUSINESS_LINE"
    RESERVE_9 = "RESERVE_9"
    RESERVE_10 = "RESERVE_10"