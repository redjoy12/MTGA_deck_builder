from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from enum import Enum



class CardType(Enum):
    """Represents the different types of Magic: The Gathering cards."""
    CREATURE = "creature"
    INSTANT = "instant"
    SORCERY = "sorcery"
    ENCHANTMENT = "enchantment"
    ARTIFACT = "artifact"
    PLANESWALKER = "planeswalker"
    LAND = "land"


class CardRole(Enum):
    """Represents the different roles a card can play in a deck."""
    WIN_CONDITION = "win_condition"
    REMOVAL = "removal"
    COUNTER = "counter"
    RAMP = "ramp"
    CARD_ADVANTAGE = "card_advantage"
    UTILITY = "utility"
    PROTECTION = "protection"
    MANA_SOURCE = "mana_source"


class DeckArchetype(Enum):
    """Represents the different deck archetypes in Magic: The Gathering."""
    AGGRO = "aggro"
    CONTROL = "control"
    MIDRANGE = "midrange"
    COMBO = "combo"
    TEMPO = "tempo"
    RAMP = "ramp"


class ManaCost(BaseModel):
    """Represents the mana cost of a card in terms of colored, generic, and total cost."""
    total: int
    colored: Dict[str, int] = Field(default_factory=dict)
    generic: int = 0

    @classmethod
    def from_string(cls, mana_cost: str) -> 'ManaCost':
        """
        Parses a mana cost string and returns a ManaCost object.

        Args:
            mana_cost (str): The mana cost string to be parsed.

        Returns:
            ManaCost: A ManaCost object representing the parsed mana cost.
        """
        colored = {color: mana_cost.count(color) for color in 'WUBRG'}
        generic = sum(int(symbol) for symbol in mana_cost if symbol.isdigit())
        total = sum(colored.values()) + generic
        return cls(total=total, colored=colored, generic=generic)


class CardBase(BaseModel):
    """Represents a basic card model used in a deck."""
    name: str
    mana_cost: Optional[ManaCost]
    cmc: float
    colors: List[str]
    quantity: int
    type_line: str
    oracle_text: str
    power: Optional[str]
    toughness: Optional[str]
    rarity: str
    role: CardRole
    set_code: str
    image_uri: Optional[str]

    class Config:
        use_enum_values = True

class DeckStatistics(BaseModel):
    """Holds statistics for a deck, including color distribution and mana curve."""
    average_cmc: float
    color_distribution: Dict[str, float]
    type_distribution: Dict[str, int]
    role_distribution: Dict[str, int]
    mana_sources_by_color: Dict[str, int]
    curve: Dict[int, int]


class DeckRequirements(BaseModel):
    """Represents the requirements or constraints for deck building."""
    colors: List[str]
    strategy: str
    format: str
    archetype: DeckArchetype
    min_creatures: Optional[int] = None
    max_creatures: Optional[int] = None
    min_lands: Optional[int] = None
    max_lands: Optional[int] = None
    required_cards: Optional[List[str]] = None
    excluded_cards: Optional[List[str]] = None
    budget_limit: Optional[float] = None
    constraints: Optional[str] = None

    @validator('colors')
    def validate_colors(cls, v):
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if not all(color in valid_colors for color in v):
            raise ValueError('Invalid color code')
        return v


class CardCreate(CardBase):
    """Schema for creating a card, including a unique identifier."""
    id: str


class CardResponse(CardBase):
    """Response schema for card information, used for API responses."""
    id: str

    class Config:
        orm_mode = True


class DeckBase(BaseModel):
    """Represents the foundational structure of a deck, including main deck and sideboard."""
    name: str
    format: str
    description: Optional[str]
    colors: List[str] = []
    strategy_tags: List[str] = []
    main_deck: List[CardBase]
    sideboard: Optional[List[CardBase]]
    lands: List[CardBase]
    statistics: DeckStatistics
    total_cards: int = Field(default=60)

    def validate_deck(self) -> List[str]:
        """
        Validates the deck according to game rules, checking card limits and deck size.

        Returns:
            List[str]: A list of validation issues, if any.
        """
        issues = []
        card_counts = Counter(card.name for card in self.main_deck + self.lands)

        # Deck size check
        if len(self.main_deck) + len(self.lands) != self.total_cards:
            issues.append(f"Deck must be exactly {self.total_cards} cards")

        # Check individual card copy limits
        for card_name, count in card_counts.items():
            if count > 4 and card_name not in ["Plains", "Island", "Swamp", "Mountain", "Forest"]:
                issues.append(f"Too many copies of {card_name}")

        return issues


class DeckResponse(DeckBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    total_card_count: Optional[int]  # New field
    # New field for color distribution
    color_distribution: Optional[Dict[str, int]]

    class Config:
        orm_mode = True
