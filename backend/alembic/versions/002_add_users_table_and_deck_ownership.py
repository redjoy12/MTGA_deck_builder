"""Add users table and deck ownership

Revision ID: 002
Revises: 001
Create Date: 2025-10-28 16:00:00.000000

"""
# pylint: disable=invalid-name
# This is an Alembic migration file and must follow Alembic's naming conventions
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op  # pylint: disable=no-name-in-module

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade the database schema:
    1. Create users table with authentication and profile fields
    2. Add user_id foreign key to decks table for ownership
    3. Create necessary indexes for performance
    """

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('NOW()')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()),
                  server_default='{}', nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes on users table
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Add user_id column to decks table
    op.add_column('decks', sa.Column('user_id', sa.Integer(), nullable=True))

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_decks_user_id',
        'decks', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Create index on user_id for faster lookups
    op.create_index('idx_decks_user_id', 'decks', ['user_id'], unique=False)


def downgrade() -> None:
    """
    Downgrade the database schema:
    1. Remove user_id from decks table
    2. Drop users table
    3. Remove all associated indexes
    """

    # Drop indexes and foreign key from decks table
    op.drop_index('idx_decks_user_id', table_name='decks')
    op.drop_constraint('fk_decks_user_id', 'decks', type_='foreignkey')
    op.drop_column('decks', 'user_id')

    # Drop users table indexes and table
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
