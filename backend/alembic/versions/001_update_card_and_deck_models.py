"""Update card and deck models with JSONB and Scryfall fields

Revision ID: 001
Revises:
Create Date: 2025-10-28 14:36:00.000000

"""
# pylint: disable=invalid-name
# This is an Alembic migration file and must follow Alembic's naming conventions
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op  # pylint: disable=no-name-in-module

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade the database schema:
    1. Change JSON columns to JSONB in cards table
    2. Add new Scryfall fields to cards table
    3. Ensure Deck JSONB columns have proper defaults
    """

    # Convert JSON columns to JSONB in cards table
    # Note: This uses USING clause to convert existing JSON data to JSONB
    op.execute("""
        ALTER TABLE cards
        ALTER COLUMN legalities TYPE JSONB USING legalities::jsonb
    """)

    op.execute("""
        ALTER TABLE cards
        ALTER COLUMN vector_embedding TYPE JSONB USING vector_embedding::jsonb
    """)

    op.execute("""
        ALTER TABLE cards
        ALTER COLUMN card_faces TYPE JSONB USING card_faces::jsonb
    """)

    # Add new Scryfall fields to cards table
    op.add_column('cards', sa.Column('scryfall_id', sa.String(), nullable=True))
    op.add_column('cards', sa.Column('oracle_id', sa.String(), nullable=True))
    op.add_column('cards', sa.Column('artist', sa.String(), nullable=True))
    op.add_column('cards', sa.Column('flavor_text', sa.String(), nullable=True))
    op.add_column('cards', sa.Column('released_at', sa.String(), nullable=True))
    op.add_column(
        'cards',
        sa.Column('prices', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'cards',
        sa.Column('produced_mana', postgresql.ARRAY(sa.String()), nullable=True)
    )
    op.add_column('cards', sa.Column('edhrec_rank', sa.Integer(), nullable=True))
    op.add_column(
        'cards',
        sa.Column('color_indicator', postgresql.ARRAY(sa.String()), nullable=True)
    )
    op.add_column('cards', sa.Column('loyalty', sa.String(), nullable=True))
    op.add_column('cards', sa.Column('hand_modifier', sa.String(), nullable=True))
    op.add_column('cards', sa.Column('life_modifier', sa.String(), nullable=True))

    # Create unique index on scryfall_id
    op.create_index('ix_cards_scryfall_id', 'cards', ['scryfall_id'], unique=True)

    # Update Deck table JSONB columns to have proper defaults if they don't exist
    # First, update any NULL values to empty JSON objects/arrays
    op.execute("""
        UPDATE decks
        SET mainboard = '{}'::jsonb
        WHERE mainboard IS NULL
    """)

    op.execute("""
        UPDATE decks
        SET sideboard = '{}'::jsonb
        WHERE sideboard IS NULL
    """)

    op.execute("""
        UPDATE decks
        SET colors = '[]'::jsonb
        WHERE colors IS NULL
    """)

    op.execute("""
        UPDATE decks
        SET strategy_tags = '[]'::jsonb
        WHERE strategy_tags IS NULL
    """)


def downgrade() -> None:
    """
    Downgrade the database schema:
    1. Remove new Scryfall fields from cards table
    2. Convert JSONB columns back to JSON
    """

    # Drop new columns
    op.drop_index('ix_cards_scryfall_id', table_name='cards')
    op.drop_column('cards', 'life_modifier')
    op.drop_column('cards', 'hand_modifier')
    op.drop_column('cards', 'loyalty')
    op.drop_column('cards', 'color_indicator')
    op.drop_column('cards', 'edhrec_rank')
    op.drop_column('cards', 'produced_mana')
    op.drop_column('cards', 'prices')
    op.drop_column('cards', 'released_at')
    op.drop_column('cards', 'flavor_text')
    op.drop_column('cards', 'artist')
    op.drop_column('cards', 'oracle_id')
    op.drop_column('cards', 'scryfall_id')

    # Convert JSONB back to JSON
    op.execute("""
        ALTER TABLE cards
        ALTER COLUMN card_faces TYPE JSON USING card_faces::json
    """)

    op.execute("""
        ALTER TABLE cards
        ALTER COLUMN vector_embedding TYPE JSON USING vector_embedding::json
    """)

    op.execute("""
        ALTER TABLE cards
        ALTER COLUMN legalities TYPE JSON USING legalities::json
    """)
