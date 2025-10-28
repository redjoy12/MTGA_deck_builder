"""Card selection agent for deck building workflow."""
import json
from typing import Any, Dict

from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agents.agent_state import AgentState
from app.core.database import CardDatabase
from app.models.card import Card, Deck
from app.models.schemas import CardRole, ManaCost
from app.utils.utils import calculate_deck_statistics


class CardSelectorAgent:
    """Agent responsible for selecting appropriate cards for the deck."""
    def __init__(self, llm: ChatGroq, db: CardDatabase):
        self.llm = llm
        self.db = db
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Magic: The Gathering card selector.
            Based on the strategy and requirements, select specific cards for the deck.

            Consider:
            1. Card synergies and interactions
            2. Mana curve optimization
            3. Color requirements and mana base needs
            4. Format legality and restrictions
            5. Budget constraints if specified

            For each card selection, provide:
            - Quantity
            - Role in the deck
            - Synergy explanations
            - Alternative options

            Output your selections in a structured format:
            ```json
            {
                "main_deck": {
                    "creatures": [{"name": string, "quantity": int, "role": string}],
                    "spells": [{"name": string, "quantity": int, "role": string}],
                    "other": [{"name": string, "quantity": int, "role": string}]
                },
                "lands": [{"name": string, "quantity": int, "role": string}],
                "sideboard": [{"name": string, "quantity": int, "role": string}]
            }
            ```"""),
            MessagesPlaceholder(variable_name="messages")
        ])

    def run(self, state: AgentState) -> AgentState:
        """Execute the card selector agent to choose appropriate cards."""
        # Get strategy details from previous messages
        ai_messages = [msg.content for msg in state.messages if isinstance(msg, AIMessage)]
        strategy_details = json.loads(ai_messages[-1])

        # Search for cards based on strategy requirements
        card_selections = {}
        for category in ["creatures", "removal", "card_advantage"]:
            if category in strategy_details["card_ratios"]:
                cards = self.db.search_cards({
                    "colors": state.requirements.colors,
                    "format": state.requirements.format,
                    "type": category,
                    "text": strategy_details["main_gameplan"]
                })
                card_selections[category] = cards

        response = self.llm.invoke(self.prompt.format(
            messages=state.messages,
            available_cards=card_selections,
            strategy=strategy_details
        ))

        # Parse card selections and create deck structure
        deck_list = json.loads(response.content)

        # Create Deck object
        main_deck = []
        for category in deck_list["main_deck"].values():
            for card in category:
                main_deck.append(Card(
                    name=card["name"],
                    quantity=card["quantity"],
                    role=card["role"],
                    **self._get_card_details(card["name"])
                ))

        lands = [Card(
            name=card["name"],
            quantity=card["quantity"],
            role=CardRole.MANA_SOURCE,
            **self._get_card_details(card["name"])
        ) for card in deck_list["lands"]]

        sideboard = [Card(
            name=card["name"],
            quantity=card["quantity"],
            role=card["role"],
            **self._get_card_details(card["name"])
        ) for card in deck_list["sideboard"]]

        state.deck = Deck(
            main_deck=main_deck,
            lands=lands,
            sideboard=sideboard,
            statistics=calculate_deck_statistics(Deck(
                main_deck=main_deck,
                lands=lands,
                sideboard=sideboard,
                total_cards=60
            ))
        )

        state.messages.append(AIMessage(content=response.content))
        state.current_agent = "optimizer"
        return state

    def _get_card_details(self, card_name: str) -> Dict[str, Any]:
        # Get card details from database
        card_data = self.db.search_cards({"text": card_name})[0]
        mana_cost = (
            ManaCost.from_string(card_data["mana_cost"])
            if card_data["mana_cost"]
            else None
        )
        return {
            "mana_cost": mana_cost,
            "type_line": card_data["type_line"],
            "cmc": card_data["cmc"],
            "color_identity": card_data["color_identity"],
            "oracle_text": card_data["oracle_text"]
        }
