"""add task status values

Revision ID: c1d7a9a4e8b2
Revises: 9c6d613e8172
Create Date: 2026-04-13 04:05:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "c1d7a9a4e8b2"
down_revision = "9c6d613e8172"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'pending'")
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'in_progress'")
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'completed'")
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'blocked'")


def downgrade() -> None:
    pass
