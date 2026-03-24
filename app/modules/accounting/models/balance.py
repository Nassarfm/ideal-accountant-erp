from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base

class AccountBalance(Base):
    __tablename__ = "account_balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    account_code = Column(String, nullable=False)

    debit_total = Column(Numeric(18, 2), default=0)
    credit_total = Column(Numeric(18, 2), default=0)
