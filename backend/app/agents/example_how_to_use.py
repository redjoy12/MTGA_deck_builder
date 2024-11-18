import asyncio
import json
from langchain_groq import ChatGroq
from backend.app.agents.agent_state import AgentState
from backend.app.agents.card_selector_agent import CardSelectorAgent
from backend.app.agents.deck_optimizer_agent import DeckOptimizerAgent
from backend.app.agents.final_review_agent import FinalReviewerAgent
from backend.app.agents.strategy_agent import StrategyAgent
from backend.app.core.database import CardDatabase
from backend.app.models.schemas import DeckRequirements
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

# Main Workflow
def create_deck_building_graph(llm: ChatGroq, db: CardDatabase) -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add agents
    workflow.add_node("strategy", StrategyAgent(llm))
    workflow.add_node("card_selector", CardSelectorAgent(llm, db))
    workflow.add_node("optimizer", DeckOptimizerAgent(llm))
    workflow.add_node("reviewer", FinalReviewerAgent(llm, db))
    
    # Define edges
    workflow.add_edge("strategy", "card_selector")
    workflow.add_edge("card_selector", "optimizer")
    workflow.add_edge("optimizer", "reviewer")
    workflow.add_edge("reviewer", "strategy")
    workflow.add_edge("reviewer", "card_selector")
    workflow.add_edge("reviewer", END)
    
    return workflow

# Example usage with additional features
async def build_deck(requirements: str):
    llm = ChatGroq(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        streaming=True
    )
    db = CardDatabase("postgresql://user:password@localhost:5432/mtga")
    
    # Parse requirements
    reqs = json.loads(requirements)
    initial_state = AgentState(
        requirements=DeckRequirements(**reqs),
        messages=[HumanMessage(content=requirements)],
        current_agent="strategy",
        db=db
    )
    
    # Create and run workflow
    workflow = create_deck_building_graph(llm, db)
    final_state = await workflow.arun(initial_state)
    
    return final_state.deck

# Example of running the system
async def main():
    requirements = {
        "colors": ["U", "B"],
        "strategy": "Control with card advantage and removal",
        "format": "Standard",
        "archetype": "control",
        "min_creatures": 8,
        "max_creatures": 12,
        "required_cards": ["Sheoldred, the Apocalypse"],
        "budget_limit": 200.0,
        "constraints": "Include at least 6 counterspells"
    }
    
    deck = await build_deck(json.dumps(requirements))
    print(json.dumps(deck.model_dump(), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
