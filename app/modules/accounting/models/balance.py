from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class AccountBalance(Base):
    __tablename__ = "account_balances"
    __table_args__ = (UniqueConstraint("account_id", "fiscal_year_id", name="uq_account_balances_account_year"),)
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_year_id = Column(Integer, ForeignKey("fiscal_years.id", ondelete="CASCADE"), nullable=False, index=True)
    account_code = Column(String(50), nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    debit_total = Column(Numeric(18, 2), nullable=False, server_default="0")
    credit_total = Column(Numeric(18, 2), nullable=False, server_default="0")
    closing_balance = Column(Numeric(18, 2), nullable=False, server_default="0")
    account = relationship("Account")
