"""journal voucher engine

Revision ID: 20260312_0004
Revises: 20260312_0003
Create Date: 2026-03-12 21:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260312_0004"
down_revision = "20260312_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "voucher_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("reset_by_fiscal_year", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("padding", sa.Integer(), nullable=False, server_default="5"),
        sa.UniqueConstraint("code", name="uq_voucher_type_code"),
    )
    op.create_index("ix_voucher_types_code", "voucher_types", ["code"])

    voucher_type_table = sa.table(
        "voucher_types",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("is_system", sa.Boolean),
        sa.column("is_active", sa.Boolean),
        sa.column("reset_by_fiscal_year", sa.Boolean),
        sa.column("padding", sa.Integer),
    )
    op.bulk_insert(
        voucher_type_table,
        [
            {"code": "JV", "name": "Journal Voucher", "description": "General journal voucher", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "PV", "name": "Payment Voucher", "description": "Payment voucher", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "RV", "name": "Receipt Voucher", "description": "Receipt voucher", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "SV", "name": "Sales Voucher", "description": "Sales voucher", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "PRV", "name": "Purchase Voucher", "description": "Purchase voucher", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "PRJ", "name": "Payroll Entry", "description": "Payroll journal entry", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "ACR", "name": "Accrual Entry", "description": "Accrual journal entry", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "EXP", "name": "Expense Entry", "description": "Expense journal entry", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "PET", "name": "Petty Cash Entry", "description": "Petty cash expense entry", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
            {"code": "REC", "name": "Recurring Entry", "description": "Recurring journal entry template base", "is_system": True, "is_active": True, "reset_by_fiscal_year": True, "padding": 5},
        ],
    )

    op.create_table(
        "document_sequences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("voucher_type_id", sa.Integer(), sa.ForeignKey("voucher_types.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fiscal_year_id", sa.Integer(), sa.ForeignKey("fiscal_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_number", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("voucher_type_id", "fiscal_year_id", name="uq_document_sequence_voucher_year"),
    )
    op.create_index("ix_document_sequences_voucher_type_id", "document_sequences", ["voucher_type_id"])
    op.create_index("ix_document_sequences_fiscal_year_id", "document_sequences", ["fiscal_year_id"])

    op.add_column("journal_entries", sa.Column("voucher_type_id", sa.Integer(), nullable=True))
    op.add_column("journal_entries", sa.Column("reference", sa.String(length=100), nullable=True))
    op.add_column("journal_entries", sa.Column("currency_code", sa.String(length=10), nullable=True))
    op.create_index("ix_journal_entries_voucher_type_id", "journal_entries", ["voucher_type_id"])
    op.create_foreign_key(
        "fk_journal_entries_voucher_type_id",
        "journal_entries",
        "voucher_types",
        ["voucher_type_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_journal_entries_voucher_type_id", "journal_entries", type_="foreignkey")
    op.drop_index("ix_journal_entries_voucher_type_id", table_name="journal_entries")
    op.drop_column("journal_entries", "currency_code")
    op.drop_column("journal_entries", "reference")
    op.drop_column("journal_entries", "voucher_type_id")

    op.drop_index("ix_document_sequences_fiscal_year_id", table_name="document_sequences")
    op.drop_index("ix_document_sequences_voucher_type_id", table_name="document_sequences")
    op.drop_table("document_sequences")

    op.drop_index("ix_voucher_types_code", table_name="voucher_types")
    op.drop_table("voucher_types")
