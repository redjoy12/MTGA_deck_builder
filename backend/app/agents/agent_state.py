from typing import List, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from app.models.card import Deck
from app.models.schemas import DeckRequirements

class AgentState(BaseModel):
    requirements: DeckRequirements
    deck: Optional[Deck] = None
    messages: List[BaseMessage]
    current_agent: str
    iteration: int = 0
    max_iterations: int = 5

    class Config:
        arbitrary_types_allowed = True