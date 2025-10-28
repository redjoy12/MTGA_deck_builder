"""Pydantic schemas for MTGA Deck Builder API."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


# -----------------------------------------
# User Resources Schemas
# -----------------------------------------

class WildcardRarity(str, Enum):
    """Enum for wildcard rarities."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"


class UserResourcesBase(BaseModel):
    """Base schema for user resources."""
    common_wildcards: int = Field(default=0, ge=0)
    uncommon_wildcards: int = Field(default=0, ge=0)
    rare_wildcards: int = Field(default=0, ge=0)
    mythic_wildcards: int = Field(default=0, ge=0)
    gold: int = Field(default=0, ge=0)
    gems: int = Field(default=0, ge=0)


class UserResourcesCreate(UserResourcesBase):
    """Schema for creating user resources."""
    user_id: str


class UserResourcesUpdate(BaseModel):
    """Schema for updating user resources (all fields optional)."""
    common_wildcards: Optional[int] = Field(None, ge=0)
    uncommon_wildcards: Optional[int] = Field(None, ge=0)
    rare_wildcards: Optional[int] = Field(None, ge=0)
    mythic_wildcards: Optional[int] = Field(None, ge=0)
    gold: Optional[int] = Field(None, ge=0)
    gems: Optional[int] = Field(None, ge=0)


class UserResourcesResponse(UserResourcesBase):
    """Response schema for user resources."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WildcardUpdate(BaseModel):
    """Schema for updating a specific wildcard."""
    rarity: WildcardRarity
    amount: int = Field(ge=0)


class CurrencyUpdate(BaseModel):
    """Schema for updating currency."""
    gold: Optional[int] = Field(None, ge=0)
    gems: Optional[int] = Field(None, ge=0)



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
    """Represents a basic card model used in a deck, aligned with database Card model."""
    id: str  # Card ID
    name: str
    mana_cost: Optional[str]  # Mana cost string (e.g., "{2}{U}{U}")
    cmc: float
    color_identity: List[str]  # Aligned with database model
    quantity: int  # Used when card is part of a deck
    type_line: str
    oracle_text: Optional[str] = ""
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    rarity: str
    set_code: str
    image_uri: Optional[str] = None
    keywords: Optional[List[str]] = []

    # Optional fields for additional functionality
    role: Optional[CardRole] = None  # Can be assigned based on card analysis

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
    def validate_colors(cls, v):  # pylint: disable=no-self-argument
        """Validate that colors are valid MTG color codes."""
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if not all(color in valid_colors for color in v):
            raise ValueError('Invalid color code')
        return v


class CardCreate(BaseModel):
    """Schema for creating a card with full Scryfall data."""
    id: str
    scryfall_id: Optional[str] = None
    oracle_id: Optional[str] = None
    name: str
    mana_cost: Optional[str] = None
    cmc: float = 0.0
    color_identity: List[str] = []
    type_line: str
    oracle_text: Optional[str] = ""
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    rarity: str
    set_code: str
    collector_number: Optional[str] = None
    artist: Optional[str] = None
    flavor_text: Optional[str] = None
    released_at: Optional[str] = None
    image_uri: Optional[str] = None
    keywords: List[str] = []
    legalities: Dict[str, str] = {}
    prices: Optional[Dict[str, str]] = None
    layout: Optional[str] = "normal"
    card_faces: Optional[Dict] = None
    back_image_uri: Optional[str] = None


class CardResponse(CardBase):
    """Response schema for card information, used for API responses."""
    scryfall_id: Optional[str] = None
    oracle_id: Optional[str] = None
    artist: Optional[str] = None
    flavor_text: Optional[str] = None
    released_at: Optional[str] = None
    legalities: Optional[Dict[str, str]] = None
    prices: Optional[Dict[str, str]] = None
    layout: Optional[str] = None

    class Config:
        orm_mode = True


class DeckBase(BaseModel):
    """
    Represents the foundational structure of a deck for API/Agent use.

    Note: This schema is optimized for agent processing and API responses.
    The database model (Deck) stores mainboard/sideboard as JSONB dicts.
    Conversion happens in the API layer.
    """
    name: str
    format: str
    description: Optional[str] = None
    colors: List[str] = []
    strategy_tags: List[str] = []

    # For agent use: cards organized by category
    main_deck: List[CardBase] = []  # Non-land spells
    sideboard: List[CardBase] = []
    lands: List[CardBase] = []  # Lands separate for easy analysis

    statistics: Optional[DeckStatistics] = None
    total_cards: int = Field(default=60)

    def validate_deck(self) -> List[str]:
        """
        Validates the deck according to game rules, checking card limits and deck size.

        Returns:
            List[str]: A list of validation issues, if any.
        """
        issues = []
        # Combine all mainboard cards (main_deck + lands)
        all_mainboard = self.main_deck + self.lands

        # Deck size check
        total_mainboard = sum(card.quantity for card in all_mainboard)
        if total_mainboard < 60:
            issues.append(f"Deck must have at least 60 cards (currently {total_mainboard})")

        # Check individual card copy limits
        basic_lands = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
        for card in all_mainboard:
            if card.quantity > 4 and card.name not in basic_lands:
                issues.append(f"Too many copies of {card.name} ({card.quantity}/4)")

        # Sideboard size check
        sideboard_total = sum(card.quantity for card in self.sideboard)
        if sideboard_total > 15:
            issues.append(f"Sideboard must have at most 15 cards (currently {sideboard_total})")

        return issues


class DeckCreate(BaseModel):
    """Schema for creating a deck."""
    name: str
    format: str
    description: Optional[str] = None
    mainboard: Dict[str, int] = {}  # {card_id: quantity}
    sideboard: Dict[str, int] = {}  # {card_id: quantity}
    colors: List[str] = []
    strategy_tags: List[str] = []

    @validator('name')
    def validate_name(cls, v):  # pylint: disable=no-self-argument
        """Validate that deck name is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Deck name cannot be empty')
        return v.strip()

    @validator('colors')
    def validate_colors(cls, v):  # pylint: disable=no-self-argument
        """Validate that colors are valid MTG color codes."""
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if not all(color in valid_colors for color in v):
            raise ValueError('Invalid color code')
        return v


class DeckResponse(BaseModel):
    """
    Response schema for deck information, used for API responses.

    This schema matches the database Deck model structure.
    For agent use, convert to DeckBase format.
    """
    id: int
    name: str
    format: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Database structure: JSONB dicts
    mainboard: Dict[str, int] = {}  # {card_id: quantity}
    sideboard: Dict[str, int] = {}  # {card_id: quantity}
    colors: List[str] = []
    strategy_tags: List[str] = []

    class Config:
        orm_mode = True

    def to_deck_base(self, card_lookup: Dict[str, 'Card']) -> DeckBase:
        """
        Convert DeckResponse to DeckBase format for agent use.

        Args:
            card_lookup: Dictionary mapping card_id to Card objects

        Returns:
            DeckBase object with cards organized into main_deck, lands, and sideboard lists
        """
        main_deck_cards = []
        land_cards = []
        sideboard_cards = []

        # Process mainboard
        for card_id, quantity in self.mainboard.items():
            card = card_lookup.get(card_id)
            if card:
                card_base = CardBase(
                    id=card.id,
                    name=card.name,
                    mana_cost=card.mana_cost,
                    cmc=card.cmc,
                    color_identity=card.color_identity or [],
                    quantity=quantity,
                    type_line=card.type_line,
                    oracle_text=card.oracle_text or "",
                    power=card.power,
                    toughness=card.toughness,
                    loyalty=card.loyalty,
                    rarity=card.rarity,
                    set_code=card.set_code,
                    image_uri=card.image_uri,
                    keywords=card.keywords or []
                )

                # Separate lands from non-lands
                if 'Land' in card.type_line:
                    land_cards.append(card_base)
                else:
                    main_deck_cards.append(card_base)

        # Process sideboard
        for card_id, quantity in self.sideboard.items():
            card = card_lookup.get(card_id)
            if card:
                card_base = CardBase(
                    id=card.id,
                    name=card.name,
                    mana_cost=card.mana_cost,
                    cmc=card.cmc,
                    color_identity=card.color_identity or [],
                    quantity=quantity,
                    type_line=card.type_line,
                    oracle_text=card.oracle_text or "",
                    power=card.power,
                    toughness=card.toughness,
                    loyalty=card.loyalty,
                    rarity=card.rarity,
                    set_code=card.set_code,
                    image_uri=card.image_uri,
                    keywords=card.keywords or []
                )
                sideboard_cards.append(card_base)

        return DeckBase(
            name=self.name,
            format=self.format,
            description=self.description,
            colors=self.colors,
            strategy_tags=self.strategy_tags,
            main_deck=main_deck_cards,
            lands=land_cards,
            sideboard=sideboard_cards
        )
