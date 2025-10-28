"""Database configuration and utility classes."""
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

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
        # pylint: disable=invalid-name
        # SessionLocal follows SQLAlchemy naming convention for session factories
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
            # pylint: disable=protected-access
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
            # pylint: disable=protected-access
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

    def get_deck(self, deck_id: int) -> Dict[str, Any]:
        """
        Retrieves a deck by its unique ID.

        Args:
            deck_id (int): The unique identifier of the deck to retrieve.

        Returns:
            Dict[str, Any]: The deck data including all fields.

        Raises:
            ValueError: If the deck with the given ID does not exist.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                SELECT
                    id, name, description, format, mainboard, sideboard,
                    colors, strategy_tags, created_at, updated_at
                FROM decks
                WHERE id = :deck_id
            """), {"deck_id": deck_id})
            row = result.fetchone()
            if row is None:
                raise ValueError(f"Deck with ID {deck_id} not found")
            # pylint: disable=protected-access
            return dict(row._mapping)

    def list_decks(
        self, limit: int = 50, offset: int = 0,
        format_filter: str = None, colors_filter: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of decks with optional filtering and pagination.

        Args:
            limit (int): Maximum number of decks to return (default: 50).
            offset (int): Number of decks to skip for pagination (default: 0).
            format_filter (str): Optional filter by format (e.g., 'Standard', 'Modern').
            colors_filter (List[str]): Optional filter by color identity.

        Returns:
            List[Dict[str, Any]]: List of deck data dictionaries.
        """
        with self.SessionLocal() as session:
            base_query = """
                SELECT
                    id, name, description, format, mainboard, sideboard,
                    colors, strategy_tags, created_at, updated_at
                FROM decks
                WHERE 1=1
            """
            conditions = []
            params = {"limit": limit, "offset": offset}

            if format_filter:
                conditions.append("format = :format_filter")
                params["format_filter"] = format_filter

            if colors_filter:
                conditions.append("colors <@ :colors_filter::jsonb")
                params["colors_filter"] = json.dumps(colors_filter)

            if conditions:
                base_query += " AND " + " AND ".join(conditions)

            base_query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

            result = session.execute(text(base_query), params)
            # pylint: disable=protected-access
            return [dict(row._mapping) for row in result]

    def update_deck(self, deck_id: int, deck_data: Dict[str, Any]):
        """
        Updates an existing deck with new data.

        Args:
            deck_id (int): The unique identifier of the deck to update.
            deck_data (Dict[str, Any]): Dictionary containing fields to update.
                Can include: name, description, format, mainboard, sideboard,
                colors, strategy_tags.

        Raises:
            ValueError: If the deck with the given ID does not exist.
        """
        with self.SessionLocal() as session:
            # Build dynamic UPDATE query based on provided fields
            set_clauses = []
            params = {"deck_id": deck_id}

            allowed_fields = [
                'name', 'description', 'format', 'mainboard',
                'sideboard', 'colors', 'strategy_tags'
            ]

            for field in allowed_fields:
                if field in deck_data:
                    if field in ['mainboard', 'sideboard', 'colors', 'strategy_tags']:
                        # JSONB fields need JSON serialization
                        set_clauses.append(f"{field} = :{field}::jsonb")
                        params[field] = json.dumps(deck_data[field])
                    else:
                        set_clauses.append(f"{field} = :{field}")
                        params[field] = deck_data[field]

            if not set_clauses:
                raise ValueError("No valid fields provided for update")

            # Always update the updated_at timestamp
            set_clauses.append("updated_at = NOW()")

            query = f"""
                UPDATE decks
                SET {', '.join(set_clauses)}
                WHERE id = :deck_id
                RETURNING id
            """

            result = session.execute(text(query), params)
            if result.rowcount == 0:
                raise ValueError(f"Deck with ID {deck_id} not found")
            session.commit()

    def delete_deck(self, deck_id: int):
        """
        Deletes a deck by its unique ID.

        Args:
            deck_id (int): The unique identifier of the deck to delete.

        Raises:
            ValueError: If the deck with the given ID does not exist.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                DELETE FROM decks
                WHERE id = :deck_id
                RETURNING id
            """), {"deck_id": deck_id})
            if result.rowcount == 0:
                raise ValueError(f"Deck with ID {deck_id} not found")
            session.commit()

    # ========== User Management Methods ==========

    def create_user(self, user_data: Dict[str, Any]) -> int:
        """
        Creates a new user account.

        Args:
            user_data (Dict[str, Any]): Dictionary containing user data.
                Required fields: username, email, password_hash
                Optional fields: is_active, is_verified, preferences

        Returns:
            int: The unique identifier of the created user.

        Raises:
            ValueError: If a user with the same email or username already exists.
        """
        with self.SessionLocal() as session:
            try:
                result = session.execute(text("""
                    INSERT INTO users (
                        username, email, password_hash, is_active,
                        is_verified, preferences, created_at
                    )
                    VALUES (
                        :username, :email, :password_hash,
                        :is_active, :is_verified, :preferences, NOW()
                    )
                    RETURNING id
                """), {
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password_hash": user_data["password_hash"],
                    "is_active": user_data.get("is_active", True),
                    "is_verified": user_data.get("is_verified", False),
                    "preferences": json.dumps(user_data.get("preferences", {}))
                })
                session.commit()
                return result.scalar_one()
            except Exception as e:
                session.rollback()
                if "unique constraint" in str(e).lower():
                    if "email" in str(e).lower():
                        raise ValueError("A user with this email already exists") from e
                    if "username" in str(e).lower():
                        raise ValueError("A user with this username already exists") from e
                raise

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieves a user by their unique ID.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            Dict[str, Any]: The user data including all fields.

        Raises:
            ValueError: If the user with the given ID does not exist.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                SELECT
                    id, username, email, password_hash, is_active,
                    is_verified, preferences, created_at, updated_at, last_login
                FROM users
                WHERE id = :user_id
            """), {"user_id": user_id})
            row = result.fetchone()
            if row is None:
                raise ValueError(f"User with ID {user_id} not found")
            # pylint: disable=protected-access
            return dict(row._mapping)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user.

        Returns:
            Optional[Dict[str, Any]]: The user data if found, None otherwise.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                SELECT
                    id, username, email, password_hash, is_active,
                    is_verified, preferences, created_at, updated_at, last_login
                FROM users
                WHERE email = :email
            """), {"email": email})
            row = result.fetchone()
            if row is None:
                return None
            # pylint: disable=protected-access
            return dict(row._mapping)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            Optional[Dict[str, Any]]: The user data if found, None otherwise.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                SELECT
                    id, username, email, password_hash, is_active,
                    is_verified, preferences, created_at, updated_at, last_login
                FROM users
                WHERE username = :username
            """), {"username": username})
            row = result.fetchone()
            if row is None:
                return None
            # pylint: disable=protected-access
            return dict(row._mapping)

    def update_user(self, user_id: int, user_data: Dict[str, Any]):
        """
        Updates an existing user with new data.

        Args:
            user_id (int): The unique identifier of the user to update.
            user_data (Dict[str, Any]): Dictionary containing fields to update.
                Can include: username, email, password_hash, is_active,
                is_verified, preferences.

        Raises:
            ValueError: If the user with the given ID does not exist or
                if trying to set a duplicate email/username.
        """
        with self.SessionLocal() as session:
            set_clauses = []
            params = {"user_id": user_id}

            allowed_fields = [
                'username', 'email', 'password_hash', 'is_active',
                'is_verified', 'preferences'
            ]

            for field in allowed_fields:
                if field in user_data:
                    if field == 'preferences':
                        set_clauses.append(f"{field} = :{field}::jsonb")
                        params[field] = json.dumps(user_data[field])
                    else:
                        set_clauses.append(f"{field} = :{field}")
                        params[field] = user_data[field]

            if not set_clauses:
                raise ValueError("No valid fields provided for update")

            set_clauses.append("updated_at = NOW()")

            query = f"""
                UPDATE users
                SET {', '.join(set_clauses)}
                WHERE id = :user_id
                RETURNING id
            """

            try:
                result = session.execute(text(query), params)
                if result.rowcount == 0:
                    raise ValueError(f"User with ID {user_id} not found")
                session.commit()
            except Exception as e:
                session.rollback()
                if "unique constraint" in str(e).lower():
                    if "email" in str(e).lower():
                        raise ValueError("A user with this email already exists") from e
                    if "username" in str(e).lower():
                        raise ValueError("A user with this username already exists") from e
                raise

    def delete_user(self, user_id: int):
        """
        Deletes a user by their unique ID.

        Args:
            user_id (int): The unique identifier of the user to delete.

        Raises:
            ValueError: If the user with the given ID does not exist.
        """
        with self.SessionLocal() as session:
            result = session.execute(text("""
                DELETE FROM users
                WHERE id = :user_id
                RETURNING id
            """), {"user_id": user_id})
            if result.rowcount == 0:
                raise ValueError(f"User with ID {user_id} not found")
            session.commit()

    def update_last_login(self, user_id: int):
        """
        Updates the last login timestamp for a user.

        Args:
            user_id (int): The unique identifier of the user.
        """
        with self.SessionLocal() as session:
            session.execute(text("""
                UPDATE users
                SET last_login = NOW()
                WHERE id = :user_id
            """), {"user_id": user_id})
            session.commit()

    def list_users(self, limit: int = 50, offset: int = 0, is_active: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of users with optional filtering and pagination.

        Args:
            limit (int): Maximum number of users to return (default: 50).
            offset (int): Number of users to skip for pagination (default: 0).
            is_active (bool): Optional filter by active status.

        Returns:
            List[Dict[str, Any]]: List of user data dictionaries.
        """
        with self.SessionLocal() as session:
            base_query = """
                SELECT
                    id, username, email, is_active, is_verified,
                    preferences, created_at, updated_at, last_login
                FROM users
                WHERE 1=1
            """
            params = {"limit": limit, "offset": offset}

            if is_active is not None:
                base_query += " AND is_active = :is_active"
                params["is_active"] = is_active

            base_query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

            result = session.execute(text(base_query), params)
            # pylint: disable=protected-access
            return [dict(row._mapping) for row in result]

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
