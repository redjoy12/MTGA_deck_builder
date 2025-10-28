from collections import Counter
from typing import Dict, List

from app.core.database import Base
from sqlalchemy import (ARRAY, JSON, Column, DateTime, Float, ForeignKey, Index, Integer,
                        String, Table, func, text)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

# Association table for deck-card relationship
deck_cards = Table(
    'deck_cards', Base.metadata,
    Column('deck_id', Integer, ForeignKey('decks.id'), primary_key=True),
    Column('card_id', String, ForeignKey('cards.id'), primary_key=True),
    Column('quantity', Integer, nullable=False)  # Required to store the number of each card in the deck
)


class Card(Base):
    """
    SQLAlchemy model representing an MTGA card with attributes for search and identification.

    Attributes:
        id (int): The unique identifier for the card.
        name (str): The name of the card.
        mana_cost (str): The mana cost of the card.
        cmc (float): The converted mana cost of the card.
        color_identity (List[str]): The colors associated with the card.
        oracle_text (str): The card's oracle text.
        type_line (str): The card's type line.
        power (str): The power value of the card (for creatures).
        toughness (str): The toughness value of the card (for creatures).
        rarity (str): The rarity of the card.
        set_code (str): The set code the card belongs to.
        collector_number (str): The collector's number for the card.
        image_uri (str): The URI for the card's image.
        keywords (List[str]): Any keywords associated with the card.
        legalities (Dict[str, str]): The legality status of the card in different formats.
        price (float): The price of the card.
        vector_embedding (Dict[str, float]): The vector embedding for the card.
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
    legalities = Column(JSON)
    price = Column(Float)
    vector_embedding = Column(JSON)
    
    # New fields for handling double-faced cards
    layout = Column(String)  # 'normal', 'transform', 'modal_dfc', etc.
    card_faces = Column(JSON)  # Store full face data as JSON
    back_image_uri = Column(String)  # Store back face image separately for convenience

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
    SQLAlchemy model representing a deck, including relationships and methods for management.

    Attributes:
        id (int): The unique identifier for the deck.
        name (str): The name of the deck.
        format (str): The format the deck is built for.
        description (str): A description of the deck.
        created_at (datetime): The date and time the deck was created.
        updated_at (datetime): The date and time the deck was last updated.
        cards (List[Card]): The cards included in the deck.
        mainboard (Dict[str, int]): The cards in the mainboard, stored as {card_id: quantity}.
        sideboard (Dict[str, int]): The cards in the sideboard, stored as {card_id: quantity}.
        colors (List[str]): The colors represented in the deck.
        strategy_tags (List[str]): Any strategy tags associated with the deck.
    """
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    format = Column(String, nullable=False, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cards = relationship("Card", secondary=deck_cards, back_populates="decks")
    mainboard = Column(JSONB)  # Store as {card_id: quantity}
    sideboard = Column(JSONB)  # Store as {card_id: quantity}
    colors = Column(JSONB)
    strategy_tags = Column(JSONB)

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

        # Initialize mainboard if empty, then add or update the card
        self.mainboard[card_id] = min(quantity, 4)

    def add_card(self, card: Card, quantity: int, sideboard: bool = False):
        """
        Adds a card to either the mainboard or sideboard based on compatibility with deck colors.

        Args:
            card (Card): The card to be added to the deck.
            quantity (int): The quantity of the card to be added.
            sideboard (bool): If True, the card is added to the sideboard; otherwise, it's added to the mainboard.

        Raises:
            ValueError: If the card's colors are incompatible with the deck's color identity.
        """
        if not set(card.color_identity or []).issubset(set(self.colors or [])):
            raise ValueError("Card colors are incompatible with deck's color identity.")

        if sideboard:
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