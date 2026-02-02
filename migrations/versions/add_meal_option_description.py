"""Add meal_option description (menu description)

Revision ID: a1b2c3d4e5f6
Revises: 2b26d7660d5d
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '2b26d7660d5d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('meal_option', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('meal_option', schema=None) as batch_op:
        batch_op.drop_column('description')
