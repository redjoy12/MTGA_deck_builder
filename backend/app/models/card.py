from sqlalchemy import Column, DateTime, Integer, String, Float, JSON, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from core.database import Base
from collections import Counter

# Association table for deck-card relationship
deck_cards = Table('deck_cards', Base.metadata,
    Column('deck_id', Integer, ForeignKey('decks.id')),
    Column('card_id', String, ForeignKey('cards.id')),
    Column('quantity', Integer)
)

class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    mana_cost = Column(String)
    cmc = Column(Float)
    colors = Column(JSON)
    type_line = Column(String)
    oracle_text = Column(String)
    power = Column(String)
    toughness = Column(String)
    rarity = Column(String)
    set_code = Column(String)
    image_uri = Column(String)
    vector_embedding = Column(JSON)
    
    decks = relationship("Deck", secondary=deck_cards, back_populates="cards")

class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    format = Column(String, nullable=False, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    cards = relationship("Card", secondary=deck_cards, back_populates="decks")
    mainboard = Column(JSON)  # Store as {card_id: quantity}
    sideboard = Column(JSON)  # Store as {card_id: quantity}
    colors = Column(JSON)
    strategy_tags = Column(JSON)

    def add_card_to_mainboard(self, card_id: str, quantity: int):
        # Ensure quantity does not exceed 4 (example business rule)
        if quantity > 4:
            raise ValueError("Cannot have more than 4 of the same card in the mainboard.")
        
        # Initialize mainboard if it's empty
        if not self.mainboard:
            self.mainboard = {}
        
        # Add or update card in mainboard
        self.mainboard[card_id] = quantity

    def add_card(self, card: Card, quantity: int):
        # Check if card colors are compatible with deck's color identity
        if not set(card.colors).issubset(set(self.colors)):
            raise ValueError("Card colors are incompatible with deck's color identity.")
        
        # Now you can proceed to add the card to mainboard or sideboard as needed
        self.add_card_to_mainboard(card.id, quantity)
    
    def get_total_card_count(self) -> int:
        """Returns the total count of cards in both mainboard and sideboard."""
        mainboard_count = sum(self.mainboard.values()) if self.mainboard else 0
        sideboard_count = sum(self.sideboard.values()) if self.sideboard else 0
        return mainboard_count + sideboard_count
    
    def get_cards_by_type(self, card_type: str):
        """Returns a list of cards in the mainboard of a specific type."""
        return [card for card in self.cards if card_type in card.type_line]
    
    def get_color_distribution(self):
        """Returns a count of each color based on the cards in the mainboard."""
        color_counter = Counter()
        
        for card in self.cards:
            for color in card.colors or []:
                color_counter[color] += 1
        
        return dict(color_counter)
    
    def get_most_frequent_cards(self):
        """Returns a list of (card_id, quantity) tuples sorted by quantity in descending order."""
        if not self.mainboard:
            return []
        return sorted(self.mainboard.items(), key=lambda item: item[1], reverse=True)