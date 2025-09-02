"""create allow/deny list tables

Revision ID: 0001
Revises: 
Create Date: 2025-09-02
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "allowed_names",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
    )
    op.create_unique_constraint("uq_allowed_names_slug", "allowed_names", ["slug"])
    op.create_index("ix_allowed_names_slug", "allowed_names", ["slug"], unique=False)

    op.create_table(
        "ban_names",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
    )
    op.create_unique_constraint("uq_ban_names_slug", "ban_names", ["slug"])
    op.create_index("ix_ban_names_slug", "ban_names", ["slug"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ban_names_slug", table_name="ban_names")
    op.drop_constraint("uq_ban_names_slug", "ban_names", type_="unique")
    op.drop_table("ban_names")

    op.drop_index("ix_allowed_names_slug", table_name="allowed_names")
    op.drop_constraint("uq_allowed_names_slug", "allowed_names", type_="unique")
    op.drop_table("allowed_names")
