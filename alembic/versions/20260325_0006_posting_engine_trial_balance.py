"""posting engine and trial balance

Revision ID: 20260325_0006
Revises: 20260312_0005
Create Date: 2026-03-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "20260325_0006"
down_revision = "20260312_0005"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "account_balances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fiscal_year_id", sa.Integer(), sa.ForeignKey("fiscal_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_code", sa.String(length=50), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=False),
        sa.Column("debit_total", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("credit_total", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("closing_balance", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.UniqueConstraint("account_id", "fiscal_year_id", name="uq_account_balances_account_year"),
    )
    op.create_index("ix_account_balances_account_id", "account_balances", ["account_id"], unique=False)
    op.create_index("ix_account_balances_fiscal_year_id", "account_balances", ["fiscal_year_id"], unique=False)
    op.create_index("ix_account_balances_account_code", "account_balances", ["account_code"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_account_balances_account_code", table_name="account_balances")
    op.drop_index("ix_account_balances_fiscal_year_id", table_name="account_balances")
    op.drop_index("ix_account_balances_account_id", table_name="account_balances")
    op.drop_table("account_balances")
