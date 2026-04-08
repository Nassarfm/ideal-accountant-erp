from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountNature(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class JournalEntryType(str, Enum):
    GJE = "GJE"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    ADJUSTMENT = "ADJUSTMENT"
    REVERSAL = "REVERSAL"


class JournalEntryStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    POSTED = "posted"
    REVERSED = "reversed"
    CANCELLED = "cancelled"


class FiscalPeriodStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class LockType(str, Enum):
    SOFT = "soft"
    HARD = "hard"
