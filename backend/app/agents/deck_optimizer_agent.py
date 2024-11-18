import json
from typing import Any, Dict, List
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from backend.app.agents.agent_state import AgentState
from backend.app.models.card import  Deck
from backend.app.utils.utils import calculate_deck_statistics, validate_mana_base


class DeckOptimizerAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Magic: The Gathering deck optimization expert.
            Review the current deck list and suggest improvements for:
            
            1. Mana curve optimization
            2. Color consistency
            3. Strategic coherence
            4. Sideboard effectiveness
            5. Common matchup preparation
            
            Analyze:
            - Card quantity ratios
            - Mana source distribution
            - Curve considerations
            - Sideboard coverage
            - Potential weaknesses
            
            Output your analysis and suggestions in a structured format:
            ```json
            {
                "analysis": {
                    "curve_issues": list[string],
                    "color_issues": list[string],
                    "strategy_issues": list[string],
                    "sideboard_issues": list[string]
                },
                "suggestions": {
                    "cards_to_remove": [{"name": string, "reason": string}],
                    "cards_to_add": [{"name": string, "reason": string}],
                    "quantity_adjustments": [{"name": string, "change": int, "reason": string}]
                }
            }
            ```"""),
            MessagesPlaceholder(variable_name="messages")
        ])
    
    def run(self, state: AgentState) -> AgentState:
        # Validate current deck
        deck_issues = state.deck.validate_deck()
        mana_issues = validate_mana_base(state.deck)
        
        response = self.llm.invoke(self.prompt.format(
            messages=state.messages,
            current_deck=state.deck.model_dump(),
            deck_issues=deck_issues,
            mana_issues=mana_issues,
            statistics=state.deck.statistics.model_dump()
        ))
        
        optimization_results = json.loads(response.content)
        
        # Apply suggested changes if any
        if optimization_results["suggestions"]["cards_to_remove"] or \
           optimization_results["suggestions"]["cards_to_add"] or \
           optimization_results["suggestions"]["quantity_adjustments"]:
            # Update deck based on suggestions
            self._apply_optimization_suggestions(state.deck, optimization_results["suggestions"])
            
            # Recalculate statistics
            state.deck.statistics = calculate_deck_statistics(state.deck)
        
        state.messages.append(AIMessage(content=response.content))
        state.current_agent = "reviewer"
        return state
    
    def _apply_optimization_suggestions(self, deck: Deck, suggestions: Dict[str, List[Dict[str, Any]]]):
        # Remove cards
        for removal in suggestions["cards_to_remove"]:
            deck.main_deck = [card for card in deck.main_deck if card.name != removal["name"]]
            deck.lands = [card for card in deck.lands if card.name != removal["name"]]
        
        # Add cards (assuming card details are fetched)
        # This would need to be implemented with proper card detail fetching
        
        # Adjust quantities
        for adjustment in suggestions["quantity_adjustments"]:
            for card_list in [deck.main_deck, deck.lands]:
                for card in card_list:
                    if card.name == adjustment["name"]:
                        card.quantity += adjustment["change"]