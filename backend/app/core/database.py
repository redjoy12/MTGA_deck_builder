"""Database configuration and utility classes."""
import json
from typing import Any, Dict, List

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Base declarative class for SQLAlchemy models
Base = declarative_base()

class CardDatabase:
    """Handles interactions with the card database for querying, saving, and updating deck data."""
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def search_cards(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches for cards matching given criteria (text, colors, cmc, type, format)."""
        with self.SessionLocal() as session:
            base_query = "SELECT * FROM cards WHERE 1=1"
            conditions, params = [], {}

            if 'text' in query:
                conditions.append(
                    "to_tsvector('english', name || ' ' || oracle_text) "
                    "@@ plainto_tsquery(:text)"
                )
                params['text'] = query['text']
            if 'colors' in query:
                conditions.append("color_identity <@ :colors")
                params['colors'] = query['colors']
            if 'cmc' in query:
                conditions.append("cmc <= :cmc")
                params['cmc'] = query['cmc']
            if 'type' in query:
                conditions.append("type_line ILIKE :type")
                params['type'] = f"%{query['type']}%"
            if 'format' in query:
                conditions.append("legalities->>:format = 'legal'")
                params['format'] = query['format']

            if conditions:
                base_query += " AND " + " AND ".join(conditions)

            result = session.execute(text(base_query), params)
            return [dict(row._mapping) for row in result]

    def save_deck(self, deck_data: Dict[str, Any]) -> int:
        """
        Saves a deck to the database and returns its unique ID.

        Args:
            deck_data (Dict[str, Any]): A dictionary containing the deck data to be saved.

        Returns:
            int: The unique identifier of the saved deck.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                INSERT INTO decks (
                    name, description, format, archetype, colors,
                    cards, created_at, performance_data
                )
                VALUES (
                    :name, :description, :format, :archetype, :colors,
                    :cards, NOW(), :performance_data
                )
                RETURNING id
            """), deck_data)
            session.commit()
            return result.scalar_one()

    def get_similar_decks(
        self, colors: List[str], archetype: str,
        format_type: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves similar decks based on colors, archetype, and format.

        Args:
            colors (List[str]): List of color identities (e.g., ['U', 'B'])
            archetype (str): Deck archetype (e.g., 'control', 'aggro')
            format_type (str): Game format (e.g., 'Standard', 'Modern')
            limit (int): Maximum number of decks to return

        Returns:
            List[Dict[str, Any]]: List of similar deck data
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                SELECT
                    id, name, description, archetype, colors,
                    cards, performance_data, created_at
                FROM decks
                WHERE
                    archetype = :archetype
                    AND format = :format_type
                    AND colors <@ :colors::jsonb
                ORDER BY created_at DESC
                LIMIT :limit
            """), {
                "archetype": archetype,
                "format_type": format_type,
                "colors": json.dumps(colors),
                "limit": limit
            })
            return [dict(row._mapping) for row in result]

    def update_deck_performance(self, deck_id: int, performance_data: Dict[str, Any]):
        """
        Updates the performance data of an existing deck based on its ID.

        Args:
            deck_id (int): The unique identifier of the deck to be updated.
            performance_data (Dict[str, Any]): A dictionary containing the new performance data.
        """
        with self.SessionLocal() as session:
            session.execute(text("""
                UPDATE decks
                SET performance_data = performance_data || :performance_data::jsonb,
                    updated_at = NOW()
                WHERE id = :deck_id
            """), {
                "deck_id": deck_id,
                "performance_data": json.dumps(performance_data)
            })
            session.commit()

DB_INSTANCE = CardDatabase(settings.get_database_url)

def get_db():
    """Dependency that provides a database session."""
    db = DB_INSTANCE.SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables based on the models."""
    Base.metadata.create_all(bind=DB_INSTANCE.engine)
