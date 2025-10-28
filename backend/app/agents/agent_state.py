from typing import Any, List, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from app.models.card import Deck
from app.models.schemas import DeckRequirements

class AgentState(BaseModel):
    requirements: DeckRequirements
    deck: Optional[Deck] = None
    messages: List[BaseMessage]
    current_agent: str
    db: Any  # Database connection (not serialized)
    iteration: int = 0
    max_iterations: int = 5