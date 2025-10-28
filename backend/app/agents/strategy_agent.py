import json
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from app.agents.agent_state import AgentState


class StrategyAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Magic: The Gathering deck building strategist expert.
            Your role is to analyze deck requirements and develop a concrete strategy.
            
            Focus on:
            1. Identifying key synergies and themes
            2. Determining optimal card ratios
            3. Planning the mana curve
            4. Identifying critical card categories (removal, card advantage, etc.)
            5. Considering the current meta and potential counter-strategies
            
            Provide specific recommendations for:
            - Creature count and characteristics
            - Spell distribution (removal, card advantage, etc.)
            - Mana base requirements
            - Key cards that fit the strategy
            - Sideboard strategy
            
            
            Output your analysis in a structured format:
            ```json
            {
                "strategy_details": {
                    "main_gameplan": string,
                    "key_synergies": list[string],
                    "card_ratios": {
                        "creatures": {"min": int, "max": int},
                        "removal": {"min": int, "max": int},
                        "card_advantage": {"min": int, "max": int},
                        ...
                    },
                    "mana_curve": {
                        "1": {"min": int, "max": int},
                        "2": {"min": int, "max": int},
                        ...
                    },
                    "key_cards": list[string],
                    "sideboard_focus": list[string]
                }
            }
            ```"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="messages")
        ])
    
    def run(self, state: AgentState) -> AgentState:
        # Get similar successful decks for reference
        similar_decks = state.db.get_similar_decks(
            state.requirements.colors,
            state.requirements.archetype,
            state.requirements.format
        )
        
        response = self.llm.invoke(self.prompt.format(
            input={
                "requirements": state.requirements.model_dump(),
                "similar_decks": similar_decks,
                "current_meta": "Current Standard meta focuses on midrange value engines and fast aggro strategies"
            },
            messages=state.messages
        ))
        
        # Parse strategy response
        strategy_details = json.loads(response.content)
        state.messages.append(AIMessage(content=json.dumps(strategy_details, indent=2)))
        state.current_agent = "card_selector"
        return state
