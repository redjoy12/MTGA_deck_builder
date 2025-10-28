"""Pydantic schemas for MTGA Deck Builder API."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator



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

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        """Validate that quantity is positive."""
        if v <= 0:
            raise ValueError('Card quantity must be positive')
        return v

    @field_validator('color_identity')
    @classmethod
    def validate_color_identity(cls, v):
        """Validate that color identity contains valid MTG colors."""
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if v and not all(color in valid_colors for color in v):
            raise ValueError('Invalid color in color_identity')
        return v

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

    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v):
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

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate that card name is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Card name cannot be empty')
        return v.strip()

    @field_validator('color_identity')
    @classmethod
    def validate_color_identity(cls, v):
        """Validate that color identity contains valid MTG colors."""
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if v and not all(color in valid_colors for color in v):
            raise ValueError('Invalid color in color_identity. Must be one of: W, U, B, R, G')
        return v

    @field_validator('cmc')
    @classmethod
    def validate_cmc(cls, v):
        """Validate that CMC is non-negative."""
        if v < 0:
            raise ValueError('Converted mana cost (CMC) cannot be negative')
        return v


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
        from_attributes = True


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

    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v):
        """Validate that colors are valid MTG color codes."""
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if not all(color in valid_colors for color in v):
            raise ValueError('Invalid color code. Must be one of: W, U, B, R, G')
        return v

    @model_validator(mode='after')
    def validate_deck_rules(self):
        """Validate deck according to MTG rules."""
        main_deck = self.main_deck
        lands = self.lands
        sideboard = self.sideboard
        deck_colors = self.colors

        # Combine all mainboard cards
        all_mainboard = main_deck + lands

        # 1. Deck size validation (minimum 60 cards)
        total_mainboard = sum(card.quantity for card in all_mainboard)
        if total_mainboard < 60:
            raise ValueError(
                f"Deck must have at least 60 cards in mainboard (currently {total_mainboard})"
            )

        # 2. Card quantity validation (max 4 except basic lands)
        basic_lands = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
        card_counts = {}
        for card in all_mainboard:
            card_counts[card.name] = card_counts.get(card.name, 0) + card.quantity

        for card_name, quantity in card_counts.items():
            if quantity > 4:
                # Check if it's a basic land by name or type_line
                is_basic_land = card_name in basic_lands
                if not is_basic_land:
                    # Double-check by finding the card in the lists
                    for card in all_mainboard:
                        if card.name == card_name:
                            if 'Basic Land' in card.type_line:
                                is_basic_land = True
                            break

                if not is_basic_land:
                    raise ValueError(
                        f"Too many copies of '{card_name}' ({quantity}). "
                        f"Maximum 4 copies allowed (except basic lands)"
                    )

        # 3. Sideboard size validation (max 15 cards)
        sideboard_total = sum(card.quantity for card in sideboard)
        if sideboard_total > 15:
            raise ValueError(
                f"Sideboard must have at most 15 cards (currently {sideboard_total})"
            )

        # 4. Color identity consistency validation
        if deck_colors:
            deck_color_set = set(deck_colors)
            for card in all_mainboard + sideboard:
                if card.color_identity:
                    card_color_set = set(card.color_identity)
                    if not card_color_set.issubset(deck_color_set):
                        raise ValueError(
                            f"Card '{card.name}' has colors {card.color_identity} "
                            f"that are not in deck colors {deck_colors}"
                        )

        # Update total_cards
        self.total_cards = total_mainboard

        return self

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

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate that deck name is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Deck name cannot be empty')
        return v.strip()

    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v):
        """Validate that colors are valid MTG color codes."""
        valid_colors = {'W', 'U', 'B', 'R', 'G'}
        if not all(color in valid_colors for color in v):
            raise ValueError('Invalid color code. Must be one of: W, U, B, R, G')
        return v

    @field_validator('mainboard')
    @classmethod
    def validate_mainboard_quantities(cls, v):
        """Validate that mainboard quantities are positive."""
        for card_id, quantity in v.items():
            if quantity <= 0:
                raise ValueError(f"Card quantity must be positive for card {card_id}")
        return v

    @field_validator('sideboard')
    @classmethod
    def validate_sideboard_quantities(cls, v):
        """Validate that sideboard quantities are positive."""
        for card_id, quantity in v.items():
            if quantity <= 0:
                raise ValueError(f"Card quantity must be positive for card {card_id}")
        return v

    @model_validator(mode='after')
    def validate_deck_creation_rules(self):
        """Validate deck creation according to MTG rules."""
        mainboard = self.mainboard
        sideboard = self.sideboard

        # 1. Validate mainboard size (minimum 60 cards)
        mainboard_total = sum(mainboard.values())
        if mainboard_total < 60:
            raise ValueError(
                f"Mainboard must have at least 60 cards (currently {mainboard_total})"
            )

        # 2. Validate sideboard size (maximum 15 cards)
        sideboard_total = sum(sideboard.values())
        if sideboard_total > 15:
            raise ValueError(
                f"Sideboard must have at most 15 cards (currently {sideboard_total})"
            )

        # Note: Card-specific validations (max 4 copies, basic lands, color identity)
        # require card data lookup and are handled at the service/API layer
        # These validators focus on structural constraints

        return self


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
        from_attributes = True

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
