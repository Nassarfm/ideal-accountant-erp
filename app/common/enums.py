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
    BANK = "BANK"
    CUSTOMER = "CUSTOMER"
    VENDOR = "VENDOR"
    ASSET = "ASSET"


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
