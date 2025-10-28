import asyncio
import json
from typing import Literal
from langchain_groq import ChatGroq
from app.agents.agent_state import AgentState
from app.agents.card_selector_agent import CardSelectorAgent
from app.agents.deck_optimizer_agent import DeckOptimizerAgent
from app.agents.final_review_agent import FinalReviewerAgent
from app.agents.strategy_agent import StrategyAgent
from app.core.database import CardDatabase
from app.models.schemas import DeckRequirements
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from app.core.config import settings


def route_reviewer(state: AgentState) -> Literal["strategy", "card_selector", "end"]:
    """Router function to determine the next node after reviewer."""
    if state.current_agent == "end":
        return "end"
    elif state.current_agent == "strategy":
        return "strategy"
    else:
        return "card_selector"


# Main Workflow
def create_deck_building_graph(llm: ChatGroq, db: CardDatabase) -> StateGraph:
    workflow = StateGraph(AgentState)

    # Initialize agents
    strategy_agent = StrategyAgent(llm, db)
    card_selector_agent = CardSelectorAgent(llm, db)
    optimizer_agent = DeckOptimizerAgent(llm)
    reviewer_agent = FinalReviewerAgent(llm, db)

    # Add agent nodes
    workflow.add_node("strategy", strategy_agent.run)
    workflow.add_node("card_selector", card_selector_agent.run)
    workflow.add_node("optimizer", optimizer_agent.run)
    workflow.add_node("reviewer", reviewer_agent.run)

    # Set entry point
    workflow.set_entry_point("strategy")

    # Define sequential edges
    workflow.add_edge("strategy", "card_selector")
    workflow.add_edge("card_selector", "optimizer")
    workflow.add_edge("optimizer", "reviewer")

    # Define conditional edges from reviewer
    workflow.add_conditional_edges(
        "reviewer",
        route_reviewer,
        {
            "strategy": "strategy",
            "card_selector": "card_selector",
            "end": END
        }
    )

    return workflow

# Example usage with additional features
async def build_deck(requirements: str):
    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0,
        streaming=True
    )
    db = CardDatabase(settings.get_database_url)

    # Parse requirements
    reqs = json.loads(requirements)
    initial_state = AgentState(
        requirements=DeckRequirements(**reqs),
        messages=[HumanMessage(content=requirements)],
        current_agent="strategy"
    )

    # Create and run workflow
    workflow = create_deck_building_graph(llm, db)
    compiled_workflow = workflow.compile()
    final_state = await compiled_workflow.ainvoke(initial_state)

    return final_state["deck"]

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
