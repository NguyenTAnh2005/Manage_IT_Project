"""expand tasks table for crud

Revision ID: 2f3b8e1a9c44
Revises: c1d7a9a4e8b2
Create Date: 2026-04-13 04:09:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "2f3b8e1a9c44"
down_revision = "c1d7a9a4e8b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DO $$ BEGIN CREATE TYPE taskpriority AS ENUM ('low', 'medium', 'high', 'critical'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.add_column("tasks", sa.Column("title", sa.String(length=255), nullable=True))
    op.add_column("tasks", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("tasks", sa.Column("priority", sa.Enum("low", "medium", "high", "critical", name="taskpriority"), nullable=True))
    op.add_column("tasks", sa.Column("created_by", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("assigned_to", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "assigned_to")
    op.drop_column("tasks", "created_by")
    op.drop_column("tasks", "priority")
    op.drop_column("tasks", "description")
    op.drop_column("tasks", "title")
