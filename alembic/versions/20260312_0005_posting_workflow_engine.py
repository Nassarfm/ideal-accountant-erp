"""posting workflow engine

Revision ID: 20260312_0005
Revises: 20260312_0004
Create Date: 2026-03-12 23:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260312_0005"
down_revision = "20260312_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("journal_entries", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("journal_entries", sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("journal_entry_id", sa.Integer(), nullable=False),
        sa.Column("journal_entry_line_id", sa.Integer(), nullable=False),
        sa.Column("entry_number", sa.String(length=50), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("fiscal_year_id", sa.Integer(), nullable=False),
        sa.Column("voucher_type_id", sa.Integer(), nullable=True),
        sa.Column("legal_entity_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("subledger_type", sa.String(length=20), nullable=False, server_default="NONE"),
        sa.Column("subledger_reference", sa.String(length=100), nullable=True),
        sa.Column("cost_center_id", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("geographic_region_id", sa.Integer(), nullable=True),
        sa.Column("business_line_id", sa.Integer(), nullable=True),
        sa.Column("reserve_dimension_9_id", sa.Integer(), nullable=True),
        sa.Column("reserve_dimension_10_id", sa.Integer(), nullable=True),
        sa.Column("debit_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("credit_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["journal_entry_line_id"], ["journal_entry_lines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fiscal_year_id"], ["fiscal_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["voucher_type_id"], ["voucher_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["legal_entity_id"], ["legal_entities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cost_center_id"], ["cost_centers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["geographic_region_id"], ["geographic_regions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["business_line_id"], ["business_lines.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reserve_dimension_9_id"], ["reserve_dimension_9_values.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reserve_dimension_10_id"], ["reserve_dimension_10_values.id"], ondelete="RESTRICT"),
    )

    for col in [
        "journal_entry_id",
        "journal_entry_line_id",
        "entry_number",
        "entry_date",
        "fiscal_year_id",
        "voucher_type_id",
        "legal_entity_id",
        "branch_id",
        "account_id",
        "posted_at",
    ]:
        op.create_index(f"ix_ledger_entries_{col}", "ledger_entries", [col], unique=False)


def downgrade() -> None:
    for col in [
        "posted_at",
        "account_id",
        "branch_id",
        "legal_entity_id",
        "voucher_type_id",
        "fiscal_year_id",
        "entry_date",
        "entry_number",
        "journal_entry_line_id",
        "journal_entry_id",
    ]:
        op.drop_index(f"ix_ledger_entries_{col}", table_name="ledger_entries")

    op.drop_table("ledger_entries")
    op.drop_column("journal_entries", "posted_at")
    op.drop_column("journal_entries", "approved_at")
