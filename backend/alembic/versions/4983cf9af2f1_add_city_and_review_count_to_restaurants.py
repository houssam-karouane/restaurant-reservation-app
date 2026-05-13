"""add city and review_count to restaurants

Revision ID: 4983cf9af2f1
Revises: 83e834274736
Create Date: 2026-05-13

"""
from alembic import op
import sqlalchemy as sa

revision = '4983cf9af2f1'
down_revision = '83e834274736'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('restaurants',
        sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('restaurants',
        sa.Column('review_count', sa.Integer(), server_default='0', nullable=False))
    op.create_index('ix_restaurants_city', 'restaurants', ['city'])


def downgrade() -> None:
    op.drop_index('ix_restaurants_city', table_name='restaurants')
    op.drop_column('restaurants', 'review_count')
    op.drop_column('restaurants', 'city') 

 