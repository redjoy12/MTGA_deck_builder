"""Add user_resources table for wildcard and currency tracking

Revision ID: 003
Revises: 002
Create Date: 2025-10-28 15:00:00.000000

"""
# pylint: disable=invalid-name
# This is an Alembic migration file and must follow Alembic's naming conventions
import sqlalchemy as sa
from alembic import op  # pylint: disable=no-name-in-module

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade the database schema:
    Create user_resources table for tracking wildcards and currency
    """
    op.create_table(
        'user_resources',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column(
            'user_id', sa.Integer(),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False, unique=True, index=True
        ),
        sa.Column('common_wildcards', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('uncommon_wildcards', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rare_wildcards', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mythic_wildcards', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('gold', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('gems', sa.Integer(), nullable=False, server_default='0'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better query performance
    op.create_index(
        'ix_user_resources_user_id',
        'user_resources',
        ['user_id'],
        unique=True
    )


def downgrade() -> None:
    """
    Downgrade the database schema:
    Drop user_resources table
    """
    op.drop_index('ix_user_resources_user_id', table_name='user_resources')
    op.drop_table('user_resources')
