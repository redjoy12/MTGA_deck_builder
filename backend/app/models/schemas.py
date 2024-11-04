from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class CardBase(BaseModel):
    name: str
    mana_cost: Optional[str]
    cmc: float
    colors: List[str]
    type_line: str
    oracle_text: str
    power: Optional[str]
    toughness: Optional[str]
    rarity: str
    set_code: str
    image_uri: Optional[str]

class CardCreate(CardBase):
    id: str

class CardResponse(CardBase):
    id: str

    class Config:
        orm_mode = True

class DeckBase(BaseModel):
    name: str
    format: str
    description: Optional[str]
    mainboard: Dict[str, int]
    sideboard: Dict[str, int]
    colors: List[str] = []
    strategy_tags: List[str] = []

class DeckCreate(DeckBase):
    pass

class DeckResponse(DeckBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    total_card_count: Optional[int]  # New field
    color_distribution: Optional[Dict[str, int]]  # New field for color distribution

    class Config:
        orm_mode = True