"""init foundation

Revision ID: 20260311_0001
Revises:
Create Date: 2026-03-11 00:00:01
"""

from alembic import op
import sqlalchemy as sa

revision = "20260311_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "health_checks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("service_name", sa.String(length=100), nullable=False, server_default="erp-backend"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ok"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("health_checks")
