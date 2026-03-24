"""accounting rules engine

Revision ID: 20260312_0003
Revises: 20260312_0002
Create Date: 2026-03-12 19:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260312_0003"
down_revision = "20260312_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("code", name="uq_bank_account_code"),
    )
    op.create_index("ix_bank_accounts_code", "bank_accounts", ["code"])

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("code", name="uq_customer_code"),
    )
    op.create_index("ix_customers_code", "customers", ["code"])

    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("code", name="uq_vendor_code"),
    )
    op.create_index("ix_vendors_code", "vendors", ["code"])

    op.create_table(
        "fixed_assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("code", name="uq_fixed_asset_code"),
    )
    op.create_index("ix_fixed_assets_code", "fixed_assets", ["code"])


def downgrade() -> None:
    op.drop_index("ix_fixed_assets_code", table_name="fixed_assets")
    op.drop_table("fixed_assets")

    op.drop_index("ix_vendors_code", table_name="vendors")
    op.drop_table("vendors")

    op.drop_index("ix_customers_code", table_name="customers")
    op.drop_table("customers")

    op.drop_index("ix_bank_accounts_code", table_name="bank_accounts")
    op.drop_table("bank_accounts")
