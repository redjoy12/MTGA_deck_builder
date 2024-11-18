import json
from typing import Literal, Union
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from backend.app.agents.agent_state import AgentState
from backend.app.core.database import CardDatabase



class FinalReviewerAgent:
    def __init__(self, llm: ChatGroq, db: CardDatabase):
        self.llm = llm
        self.db = db
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Magic: The Gathering final deck reviewer.
            Perform a comprehensive review of the deck, checking:
            
            1. Adherence to format rules and restrictions
            2. Strategic coherence and game plan clarity
            3. Mana base stability
            4. Sideboard effectiveness
            5. Budget constraints (if applicable)
            
            Provide a final assessment with:
            - Overall deck rating (1-10)
            - Key strengths
            - Potential weaknesses
            - Matchup predictions
            - Improvement suggestions
            
            Output your review in a structured format:
            ```json
            {
                "review": {
                    "rating": int,
                    "strengths": list[string],
                    "weaknesses": list[string],
                    "matchups": {
                        "favorable": list[string],
                        "unfavorable": list[string]
                    }
                },
                "decision": "APPROVE" | "REVISE_STRATEGY" | "NEEDS_OPTIMIZATION",
                "reasons": list[string]
            }
            ```"""),
            MessagesPlaceholder(variable_name="messages")
        ])
    
    def run(self, state: AgentState) -> Union[AgentState, Literal["end"], Literal["strategy"]]:
        response = self.llm.invoke(self.prompt.format(
            messages=state.messages,
            current_deck=state.deck.model_dump(),
            requirements=state.requirements.model_dump()
        ))
        
        review_results = json.loads(response.content)
        
        # Check iteration limit
        state.iteration += 1
        if state.iteration >= state.max_iterations:
            review_results["decision"] = "APPROVE"
            review_results["reasons"].append("Maximum iteration limit reached")
        
        if review_results["decision"] == "APPROVE":
            # Save deck to database with review data
            deck_data = {
                "name": f"{state.requirements.archetype.value} {'-'.join(state.requirements.colors)}",
                "description": json.dumps(review_results["review"]),
                "format": state.requirements.format,
                "archetype": state.requirements.archetype.value,
                "colors": state.requirements.colors,
                "cards": state.deck.model_dump(),
                "performance_data": {
                    "predicted_rating": review_results["review"]["rating"],
                    "favorable_matchups": review_results["review"]["matchups"]["favorable"],
                    "unfavorable_matchups": review_results["review"]["matchups"]["unfavorable"]
                }
            }
            self.db.save_deck(deck_data)
            return "end"
        elif review_results["decision"] == "REVISE_STRATEGY":
            state.messages.append(AIMessage(content=json.dumps(review_results, indent=2)))
            return "strategy"
        else:
            state.messages.append(AIMessage(content=json.dumps(review_results, indent=2)))
            return "card_selector"