"""SQLAlchemy models for cards, decks, and users."""
from collections import Counter
from typing import Dict, List

from sqlalchemy import (
    ARRAY, Column, DateTime, Float, ForeignKey, Index, Integer,
    String, Table, Boolean, func, text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base

# Association table for deck-card relationship
deck_cards = Table(
    'deck_cards', Base.metadata,
    Column('deck_id', Integer, ForeignKey('decks.id'), primary_key=True),
    Column('card_id', String, ForeignKey('cards.id'), primary_key=True),
    # Stores the number of each card in the deck
    Column('quantity', Integer, nullable=False)
)


class Card(Base):
    """
    SQLAlchemy model representing an MTGA card with comprehensive Scryfall data.

    Attributes:
        id (str): The unique identifier for the card (Arena ID).
        scryfall_id (str): The Scryfall UUID for this card.
        oracle_id (str): Oracle ID shared across card variants.
        name (str): The name of the card.
        mana_cost (str): The mana cost of the card.
        cmc (float): The converted mana cost of the card.
        color_identity (List[str]): The colors associated with the card.
        color_indicator (List[str]): Color indicator for cards without mana cost.
        oracle_text (str): The card's oracle text.
        type_line (str): The card's type line.
        power (str): The power value of the card (for creatures).
        toughness (str): The toughness value of the card (for creatures).
        loyalty (str): Loyalty value for planeswalkers.
        rarity (str): The rarity of the card.
        set_code (str): The set code the card belongs to.
        collector_number (str): The collector's number for the card.
        artist (str): The artist who illustrated the card.
        flavor_text (str): The flavor text of the card.
        released_at (str): Release date in YYYY-MM-DD format.
        image_uri (str): The URI for the card's image.
        keywords (List[str]): Any keywords associated with the card.
        legalities (Dict[str, str]): The legality status of the card in different formats (JSONB).
        price (float): The primary price of the card.
        prices (Dict[str, str]): Complete price data from Scryfall (JSONB).
        produced_mana (List[str]): Colors of mana this card can produce.
        edhrec_rank (int): Commander popularity rank.
        vector_embedding (Dict[str, float]): The vector embedding for the card (JSONB).
        layout (str): Card layout type ('normal', 'transform', 'modal_dfc', etc.).
        card_faces (Dict): Full data for double-faced cards (JSONB).
        back_image_uri (str): Image URI for the back face of double-faced cards.
        hand_modifier (str): Hand size modifier for Vanguard cards.
        life_modifier (str): Life total modifier for Vanguard cards.
        decks (List[Deck]): The decks the card is associated with.
    """
    __tablename__ = "cards"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    mana_cost = Column(String)
    cmc = Column(Float)
    color_identity = Column(ARRAY(String))
    oracle_text = Column(String)
    type_line = Column(String)
    power = Column(String)
    toughness = Column(String)
    rarity = Column(String)
    set_code = Column(String)
    collector_number = Column(String)
    image_uri = Column(String)
    keywords = Column(ARRAY(String))
    legalities = Column(JSONB)  # Use JSONB for better PostgreSQL performance
    price = Column(Float)
    vector_embedding = Column(JSONB)  # Use JSONB for better PostgreSQL performance

    # New fields for handling double-faced cards
    layout = Column(String)  # 'normal', 'transform', 'modal_dfc', etc.
    card_faces = Column(JSONB)  # Store full face data as JSONB
    back_image_uri = Column(String)  # Store back face image separately for convenience

    # Additional Scryfall fields
    scryfall_id = Column(String, unique=True, index=True)  # Official Scryfall UUID
    oracle_id = Column(String)  # Oracle ID for card variants
    artist = Column(String)
    flavor_text = Column(String)
    released_at = Column(String)  # Date string in YYYY-MM-DD format
    prices = Column(JSONB)  # Complete price data from Scryfall (usd, usd_foil, eur, tix)
    produced_mana = Column(ARRAY(String))  # Colors of mana this card can produce
    edhrec_rank = Column(Integer)  # Commander popularity rank
    color_indicator = Column(ARRAY(String))  # For cards with color indicator
    loyalty = Column(String)  # For planeswalkers
    hand_modifier = Column(String)  # For Vanguard cards
    life_modifier = Column(String)  # For Vanguard cards

    decks = relationship("Deck", secondary=deck_cards, back_populates="cards")

    __table_args__ = (
        Index('idx_cards_text_search',
              text("to_tsvector('english', name || ' ' || COALESCE(oracle_text, ''))")),
        Index('idx_cards_color_identity', color_identity, postgresql_using='gin'),
        Index('idx_cards_cmc', cmc),
        Index('idx_cards_type_line', type_line),
    )

class Deck(Base):
    """
    SQLAlchemy model representing a deck with JSONB storage for mainboard/sideboard.

    The deck composition is stored in JSONB columns for efficient querying and updates.
    Mainboard includes both spells and lands. Sideboard is separate.

    Attributes:
        id (int): The unique identifier for the deck.
        name (str): The name of the deck.
        format (str): The format the deck is built for (Standard, Modern, etc.).
        description (str): A description of the deck strategy.
        created_at (datetime): The date and time the deck was created.
        updated_at (datetime): The date and time the deck was last updated.
        mainboard (Dict[str, int]): Cards in the mainboard, stored as {card_id: quantity} (JSONB).
        sideboard (Dict[str, int]): Cards in the sideboard, stored as {card_id: quantity} (JSONB).
        colors (List[str]): The color identity of the deck (JSONB).
        strategy_tags (List[str]): Strategy tags for deck categorization (JSONB).
        cards (List[Card]): Relationship to Card objects (maintained for backwards compatibility).

    Note:
        The mainboard should include all 60+ cards (creatures, spells, and lands).
        Lands are not stored separately in the database but can be filtered by type_line.
    """
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    format = Column(String, nullable=False, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Deck composition stored as JSONB for efficiency
    mainboard = Column(JSONB, default=dict)  # {card_id: quantity}
    sideboard = Column(JSONB, default=dict)  # {card_id: quantity}
    colors = Column(JSONB, default=list)  # ['W', 'U', 'B', 'R', 'G']
    strategy_tags = Column(JSONB, default=list)  # ['aggro', 'tempo', etc.]

    # User relationship
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    owner = relationship("User", back_populates="decks")

    # Relationship to cards (for backwards compatibility and ORM conveniences)
    cards = relationship("Card", secondary=deck_cards, back_populates="decks")

    __table_args__ = (
        Index('idx_decks_colors', colors, postgresql_using='gin'),
        Index('idx_decks_format', format),
    )

    def add_card_to_mainboard(self, card_id: str, quantity: int):
        """
        Adds a card to the mainboard with a specified quantity.

        Args:
            card_id (str): The unique identifier of the card to be added.
            quantity (int): The quantity of the card to be added.

        Raises:
            ValueError: If the quantity exceeds 4, except for basic lands.
        """
        if quantity > 4 and card_id not in ["Plains", "Island", "Swamp", "Mountain", "Forest"]:
            raise ValueError("Cannot have more than 4 of the same card in the mainboard.")

        # Initialize mainboard if None
        if self.mainboard is None:
            self.mainboard = {}

        # Add or update the card
        self.mainboard[card_id] = min(quantity, 4)

    def add_card(self, card: Card, quantity: int, sideboard: bool = False):
        """
        Adds a card to either the mainboard or sideboard based on compatibility with deck colors.

        Args:
            card (Card): The card to be added to the deck.
            quantity (int): The quantity of the card to be added.
            sideboard (bool): If True, the card is added to the sideboard;
                otherwise, it's added to the mainboard.

        Raises:
            ValueError: If the card's colors are incompatible with the deck's color identity.
        """
        if not set(card.color_identity or []).issubset(set(self.colors or [])):
            raise ValueError("Card colors are incompatible with deck's color identity.")

        if sideboard:
            # Initialize sideboard if None
            if self.sideboard is None:
                self.sideboard = {}
            self.sideboard[card.id] = quantity
        else:
            self.add_card_to_mainboard(card.id, quantity)

    def get_total_card_count(self) -> int:
        """
        Returns the total number of cards in both mainboard and sideboard.

        Returns:
            int: The total number of cards in the deck.
        """
        mainboard_count = sum(self.mainboard.values()) if self.mainboard else 0
        sideboard_count = sum(self.sideboard.values()) if self.sideboard else 0
        return mainboard_count + sideboard_count

    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """
        Returns a list of cards in the mainboard that match a specified type.

        Args:
            card_type (str): The type of cards to retrieve.

        Returns:
            List[Card]: A list of cards matching the specified type.
        """
        return [card for card in self.cards if card_type.lower() in (card.type_line or "").lower()]

    def get_color_distribution(self) -> Dict[str, int]:
        """
        Returns a color distribution count based on the mainboard cards.

        Returns:
            Dict[str, int]: A dictionary representing the color distribution of the deck.
        """
        color_counter = Counter()
        for card_id, quantity in self.mainboard.items():
            card = next((c for c in self.cards if c.id == card_id), None)
            if card:
                for color in card.color_identity or []:
                    color_counter[color] += quantity
        return dict(color_counter)

    def get_most_frequent_cards(self, n: int = 5) -> List[tuple]:
        """
        Returns the top `n` cards from the mainboard, sorted by quantity.

        Args:
            n (int): The number of top cards to return.

        Returns:
            List[tuple]: A list of tuples, where each tuple contains the card ID and its quantity.
        """
        if not self.mainboard:
            return []
        return sorted(self.mainboard.items(), key=lambda item: item[1], reverse=True)[:n]


class User(Base):
    """
    SQLAlchemy model representing a user account.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The unique username for the user.
        email (str): The unique email address for the user.
        password_hash (str): The hashed password for authentication.
        is_active (bool): Whether the user account is active.
        is_verified (bool): Whether the user's email has been verified.
        created_at (datetime): The date and time the user was created.
        updated_at (datetime): The date and time the user was last updated.
        last_login (datetime): The date and time of the user's last login.
        preferences (Dict[str, Any]): User preferences and settings (JSONB).
        decks (List[Deck]): The decks owned by this user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # User preferences stored as JSONB
    preferences = Column(JSONB, default=dict)  # Theme, default format, etc.

    # Relationship to decks
    decks = relationship("Deck", back_populates="owner")

    __table_args__ = (
        Index('idx_users_email', email),
        Index('idx_users_username', username),
    )
