"""accounting core

Revision ID: 20260312_0002
Revises: 20260311_0001
Create Date: 2026-03-12 00:00:02
"""

from alembic import op
import sqlalchemy as sa

revision = "20260312_0002"
down_revision = "20260311_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "legal_entities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_legal_entities_code", "legal_entities", ["code"], unique=True)
    op.create_unique_constraint("uq_legal_entities_name", "legal_entities", ["name"])

    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("legal_entity_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["legal_entity_id"], ["legal_entities.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_branches_legal_entity_id", "branches", ["legal_entity_id"], unique=False)
    op.create_unique_constraint("uq_branch_legal_entity_code", "branches", ["legal_entity_id", "code"])

    op.create_table(
        "dimension_definitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=False),
        sa.Column("name_ar", sa.String(length=100), nullable=False),
        sa.Column("is_reserved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("sort_order"),
        sa.UniqueConstraint("code"),
    )

    simple_tables = [
        "cost_centers",
        "departments",
        "projects",
        "geographic_regions",
        "business_lines",
        "reserve_dimension_9_values",
        "reserve_dimension_10_values",
    ]
    for table in simple_tables:
        op.create_table(
            table,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(length=30), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.create_index(f"ix_{table}_code", table, ["code"], unique=False)
        op.create_unique_constraint(f"uq_{table}_code", table, ["code"])

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name_ar", sa.String(length=200), nullable=False),
        sa.Column("name_en", sa.String(length=200), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("account_type", sa.String(length=20), nullable=False),
        sa.Column("financial_statement_type", sa.String(length=10), nullable=False),
        sa.Column("normal_balance", sa.String(length=10), nullable=False),
        sa.Column("is_postable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_subledger", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("subledger_type", sa.String(length=20), nullable=False, server_default="NONE"),
        sa.Column("allow_manual_entry", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("allow_reconciliation", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("account_type IN ('ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE')", name="ck_accounts_account_type"),
        sa.CheckConstraint("financial_statement_type IN ('BS','PL')", name="ck_accounts_financial_statement_type"),
        sa.CheckConstraint("normal_balance IN ('DR','CR')", name="ck_accounts_normal_balance"),
        sa.CheckConstraint("subledger_type IN ('NONE','BANK','CUSTOMER','VENDOR','ASSET')", name="ck_accounts_subledger_type"),
        sa.ForeignKeyConstraint(["parent_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("code", name="uq_account_code"),
    )
    op.create_index("ix_accounts_code", "accounts", ["code"], unique=False)
    op.create_index("ix_accounts_level", "accounts", ["level"], unique=False)
    op.create_index("ix_accounts_parent_id", "accounts", ["parent_id"], unique=False)

    op.create_table(
        "account_dimension_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("dimension_code", sa.String(length=30), nullable=False),
        sa.Column("is_allowed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.CheckConstraint("dimension_code IN ('LEGAL_ENTITY','BRANCH','MAIN_ACCOUNT','COST_CENTER','DEPARTMENT','PROJECT','GEOGRAPHIC_REGION','BUSINESS_LINE','RESERVE_9','RESERVE_10')", name="ck_account_dimension_rules_dimension_code"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("account_id", "dimension_code", name="uq_account_dimension_rule"),
    )
    op.create_index("ix_account_dimension_rules_account_id", "account_dimension_rules", ["account_id"], unique=False)

    op.create_table(
        "fiscal_years",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("name", name="uq_fiscal_year_name"),
    )
    op.create_index("ix_fiscal_years_name", "fiscal_years", ["name"], unique=False)

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_number", sa.String(length=50), nullable=False),
        sa.Column("fiscal_year_id", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("status IN ('DRAFT','POSTED','VOID')", name="ck_journal_entries_status"),
        sa.ForeignKeyConstraint(["fiscal_year_id"], ["fiscal_years.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_journal_entries_entry_number", "journal_entries", ["entry_number"], unique=True)
    op.create_index("ix_journal_entries_entry_date", "journal_entries", ["entry_date"], unique=False)
    op.create_index("ix_journal_entries_fiscal_year_id", "journal_entries", ["fiscal_year_id"], unique=False)

    op.create_table(
        "journal_entry_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("journal_entry_id", sa.Integer(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("legal_entity_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("cost_center_id", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("geographic_region_id", sa.Integer(), nullable=True),
        sa.Column("business_line_id", sa.Integer(), nullable=True),
        sa.Column("reserve_dimension_9_id", sa.Integer(), nullable=True),
        sa.Column("reserve_dimension_10_id", sa.Integer(), nullable=True),
        sa.Column("subledger_type", sa.String(length=20), nullable=False, server_default="NONE"),
        sa.Column("subledger_reference", sa.String(length=100), nullable=True),
        sa.Column("line_description", sa.String(length=500), nullable=True),
        sa.Column("debit_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("credit_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.CheckConstraint("subledger_type IN ('NONE','BANK','CUSTOMER','VENDOR','ASSET')", name="ck_journal_entry_lines_subledger_type"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
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
    for col in ["journal_entry_id", "legal_entity_id", "branch_id", "account_id"]:
        op.create_index(f"ix_journal_entry_lines_{col}", "journal_entry_lines", [col], unique=False)

    op.bulk_insert(
        sa.table(
            "dimension_definitions",
            sa.column("sort_order", sa.Integer()),
            sa.column("code", sa.String()),
            sa.column("name_en", sa.String()),
            sa.column("name_ar", sa.String()),
            sa.column("is_reserved", sa.Boolean()),
            sa.column("is_active", sa.Boolean()),
        ),
        [
            {"sort_order": 1, "code": "LEGAL_ENTITY", "name_en": "Legal Entity", "name_ar": "الشركة / الكيان القانوني", "is_reserved": False, "is_active": True},
            {"sort_order": 2, "code": "BRANCH", "name_en": "Branch", "name_ar": "الفرع", "is_reserved": False, "is_active": True},
            {"sort_order": 3, "code": "MAIN_ACCOUNT", "name_en": "Main Account", "name_ar": "رقم الحساب الرئيسي", "is_reserved": False, "is_active": True},
            {"sort_order": 4, "code": "COST_CENTER", "name_en": "Cost Center", "name_ar": "مركز التكلفة", "is_reserved": False, "is_active": True},
            {"sort_order": 5, "code": "DEPARTMENT", "name_en": "Department", "name_ar": "القسم / الإدارة", "is_reserved": False, "is_active": True},
            {"sort_order": 6, "code": "PROJECT", "name_en": "Project / Job Order", "name_ar": "المشروع / أمر العمل", "is_reserved": False, "is_active": True},
            {"sort_order": 7, "code": "GEOGRAPHIC_REGION", "name_en": "Geographic Region", "name_ar": "المنطقة الجغرافية", "is_reserved": False, "is_active": True},
            {"sort_order": 8, "code": "BUSINESS_LINE", "name_en": "Business Line / Product", "name_ar": "خط الأعمال / المنتج", "is_reserved": False, "is_active": True},
            {"sort_order": 9, "code": "RESERVE_9", "name_en": "Reserve Dimension 9", "name_ar": "البعد الاحتياطي 9", "is_reserved": True, "is_active": True},
            {"sort_order": 10, "code": "RESERVE_10", "name_en": "Reserve Dimension 10", "name_ar": "البعد الاحتياطي 10", "is_reserved": True, "is_active": True},
        ],
    )


def downgrade() -> None:
    for idx in ["ix_journal_entry_lines_journal_entry_id", "ix_journal_entry_lines_legal_entity_id", "ix_journal_entry_lines_branch_id", "ix_journal_entry_lines_account_id"]:
        op.drop_index(idx, table_name="journal_entry_lines")
    op.drop_table("journal_entry_lines")
    op.drop_index("ix_journal_entries_fiscal_year_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_entry_date", table_name="journal_entries")
    op.drop_index("ix_journal_entries_entry_number", table_name="journal_entries")
    op.drop_table("journal_entries")
    op.drop_index("ix_fiscal_years_name", table_name="fiscal_years")
    op.drop_table("fiscal_years")
    op.drop_index("ix_account_dimension_rules_account_id", table_name="account_dimension_rules")
    op.drop_table("account_dimension_rules")
    op.drop_index("ix_accounts_parent_id", table_name="accounts")
    op.drop_index("ix_accounts_level", table_name="accounts")
    op.drop_index("ix_accounts_code", table_name="accounts")
    op.drop_table("accounts")
    for table in [
        "reserve_dimension_10_values",
        "reserve_dimension_9_values",
        "business_lines",
        "geographic_regions",
        "projects",
        "departments",
        "cost_centers",
    ]:
        op.drop_constraint(f"uq_{table}_code", table, type_="unique")
        op.drop_index(f"ix_{table}_code", table_name=table)
        op.drop_table(table)
    op.drop_table("dimension_definitions")
    op.drop_constraint("uq_branch_legal_entity_code", "branches", type_="unique")
    op.drop_index("ix_branches_legal_entity_id", table_name="branches")
    op.drop_table("branches")
    op.drop_constraint("uq_legal_entities_name", "legal_entities", type_="unique")
    op.drop_index("ix_legal_entities_code", table_name="legal_entities")
    op.drop_table("legal_entities")
