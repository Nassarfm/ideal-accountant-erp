from sqlalchemy import Column, String, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), nullable=False)

    account_code = Column(String, nullable=False)
    entry_date = Column(Date, nullable=False)

    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)

    description = Column(String, nullable=True)
