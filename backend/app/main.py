"""Main FastAPI application for MTGA AI Deck Builder."""
import json
from typing import Optional, List

import uvicorn

from fastapi import (
    Depends, FastAPI, HTTPException, status,
    WebSocket, WebSocketDisconnect, Query
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from app.core.database import get_db, CardDatabase
from app.core.config import settings
from app.models.card import Card, Deck
from app.models.user_resources import UserResources
from app.models.schemas import (
    CardCreate, CardResponse, DeckCreate, DeckResponse,
    DeckRequirements, UserResourcesCreate, UserResourcesUpdate,
    UserResourcesResponse, WildcardUpdate, CurrencyUpdate
)
from app.agents.agent_state import AgentState
from app.agents.card_selector_agent import CardSelectorAgent
from app.agents.deck_optimizer_agent import DeckOptimizerAgent
from app.agents.final_review_agent import FinalReviewerAgent
from app.agents.strategy_agent import StrategyAgent

app = FastAPI(
    title="MTGA AI Deck Builder",
    description="An AI-powered deck building assistant for Magic: The Gathering Arena",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------
# Helper Functions
# -----------------------------------------

def convert_card_to_response(card: Card) -> CardResponse:
    """Convert ORM Card object to CardResponse schema."""
    return CardResponse(
        id=card.id,
        name=card.name,
        mana_cost=card.mana_cost,
        cmc=card.cmc or 0.0,
        color_identity=card.color_identity or [],
        quantity=1,  # Default quantity
        type_line=card.type_line,
        oracle_text=card.oracle_text or "",
        power=card.power,
        toughness=card.toughness,
        loyalty=card.loyalty,
        rarity=card.rarity,
        set_code=card.set_code,
        image_uri=card.image_uri,
        keywords=card.keywords or [],
        scryfall_id=card.scryfall_id,
        oracle_id=card.oracle_id,
        artist=card.artist,
        flavor_text=card.flavor_text,
        released_at=card.released_at,
        legalities=card.legalities,
        prices=card.prices,
        layout=card.layout
    )

def convert_deck_to_response(deck: Deck) -> DeckResponse:
    """Convert ORM Deck object to DeckResponse schema."""
    return DeckResponse(
        id=deck.id,
        name=deck.name,
        format=deck.format,
        description=deck.description,
        created_at=deck.created_at,
        updated_at=deck.updated_at,
        mainboard=deck.mainboard or {},
        sideboard=deck.sideboard or {},
        colors=deck.colors or [],
        strategy_tags=deck.strategy_tags or []
    )

def create_deck_building_graph(llm: ChatGroq, db: CardDatabase) -> StateGraph:
    """Create the deck building workflow graph."""
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
    def route_reviewer(state: AgentState):
        if state.current_agent == "end":
            return "end"
        if state.current_agent == "strategy":
            return "strategy"
        return "card_selector"

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

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint for the API.

    Returns:
        dict: A welcome message indicating the API is available.
    """
    return {"message": "Welcome to MTGA AI Deck Builder API"}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify if the API is running.

    Returns:
        dict: Status indicating that the API is healthy.
    """
    return {"status": "healthy"}

# -----------------------------------------
# Deck Endpoints
# -----------------------------------------

@app.post(
    "/decks",
    response_model=DeckResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Decks"]
)
def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    """
    Create a new deck with specified attributes.

    Args:
        deck (DeckCreate): A Pydantic model containing deck creation data.
        db (Session): Database session dependency.

    Returns:
        DeckResponse: The created deck details, including all attributes.

    Raises:
        HTTPException: If there's a database error or integrity constraint violation.
    """
    try:
        db_deck = Deck(**deck.dict())
        db.add(db_deck)
        db.commit()
        db.refresh(db_deck)
        return convert_deck_to_response(db_deck)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deck with this name already exists: {str(e)}"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.get("/decks/{deck_id}", response_model=DeckResponse, tags=["Decks"])
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a deck by its ID.

    Args:
        deck_id (int): The ID of the deck to retrieve.
        db (Session): Database session dependency.

    Returns:
        DeckResponse: The deck details.

    Raises:
        HTTPException: If the deck with the specified ID is not found.
    """
    try:
        db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not db_deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck with id {deck_id} not found"
            )
        return convert_deck_to_response(db_deck)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.get("/decks", response_model=List[DeckResponse], tags=["Decks"])
def list_decks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    deck_format: Optional[str] = Query(None, description="Filter by format"),
    db: Session = Depends(get_db)
):
    """
    List all decks in the database with optional filtering and pagination.

    Args:
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.
        deck_format (str, optional): Filter decks by format.
        db (Session): Database session dependency.

    Returns:
        List[DeckResponse]: A list of decks matching the criteria.

    Raises:
        HTTPException: If there's a database error.
    """
    try:
        query = db.query(Deck)
        if deck_format:
            query = query.filter(Deck.format == deck_format)
        decks = query.offset(skip).limit(limit).all()
        return [convert_deck_to_response(deck) for deck in decks]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.put("/decks/{deck_id}", response_model=DeckResponse, tags=["Decks"])
def update_deck(deck_id: int, deck: DeckCreate, db: Session = Depends(get_db)):
    """
    Update an existing deck.

    Args:
        deck_id (int): The ID of the deck to update.
        deck (DeckCreate): Updated deck data.
        db (Session): Database session dependency.

    Returns:
        DeckResponse: The updated deck details.

    Raises:
        HTTPException: If the deck is not found or there's a database error.
    """
    try:
        db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not db_deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck with id {deck_id} not found"
            )

        # Update fields
        for key, value in deck.dict(exclude_unset=True).items():
            setattr(db_deck, key, value)

        db.commit()
        db.refresh(db_deck)
        return convert_deck_to_response(db_deck)
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deck name already exists: {str(e)}"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.delete("/decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Decks"])
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    """
    Delete a deck by its ID.

    Args:
        deck_id (int): The ID of the deck to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the deck is not found or there's a database error.
    """
    try:
        db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not db_deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck with id {deck_id} not found"
            )

        db.delete(db_deck)
        db.commit()
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

# -----------------------------------------
# Card Endpoints
# -----------------------------------------

@app.post(
    "/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Cards"]
)
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    """
    Create a new card with specified attributes.

    Args:
        card (CardCreate): A Pydantic model containing card creation data.
        db (Session): Database session dependency.

    Returns:
        CardResponse: The created card details, including all attributes.

    Raises:
        HTTPException: If there's a database error or integrity constraint violation.
    """
    try:
        db_card = Card(**card.dict())
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return convert_card_to_response(db_card)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Card with this ID already exists: {str(e)}"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.get("/cards/{card_id}", response_model=CardResponse, tags=["Cards"])
def get_card(card_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a card by its ID.

    Args:
        card_id (str): The unique identifier of the card to retrieve.
        db (Session): Database session dependency.

    Returns:
        CardResponse: The card details.

    Raises:
        HTTPException: If the card with the specified ID is not found.
    """
    try:
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if not db_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with id {card_id} not found"
            )
        return convert_card_to_response(db_card)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.get("/cards", response_model=List[CardResponse], tags=["Cards"])
# pylint: disable=R0917,R0913
# FastAPI endpoint requires multiple query parameters
def list_cards(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by card name (partial match)"),
    type_line: Optional[str] = Query(None, description="Filter by type line (partial match)"),
    colors: Optional[str] = Query(
        None, description="Filter by color identity (comma-separated: W,U,B,R,G)"
    ),
    rarity: Optional[str] = Query(None, description="Filter by rarity"),
    db: Session = Depends(get_db)
):
    """
    List all cards in the database with optional filtering and pagination.

    Args:
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.
        name (str, optional): Filter by card name (partial match).
        type_line (str, optional): Filter by type line (partial match).
        colors (str, optional): Filter by color identity.
        rarity (str, optional): Filter by rarity.
        db (Session): Database session dependency.

    Returns:
        List[CardResponse]: A list of cards matching the criteria.

    Raises:
        HTTPException: If there's a database error.
    """
    try:
        query = db.query(Card)

        if name:
            query = query.filter(Card.name.ilike(f"%{name}%"))
        if type_line:
            query = query.filter(Card.type_line.ilike(f"%{type_line}%"))
        if colors:
            color_list = colors.split(",")
            query = query.filter(Card.color_identity.contains(color_list))
        if rarity:
            query = query.filter(Card.rarity == rarity)

        cards = query.offset(skip).limit(limit).all()
        return [convert_card_to_response(card) for card in cards]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.put("/cards/{card_id}", response_model=CardResponse, tags=["Cards"])
def update_card(card_id: str, card: CardCreate, db: Session = Depends(get_db)):
    """
    Update an existing card.

    Args:
        card_id (str): The ID of the card to update.
        card (CardCreate): Updated card data.
        db (Session): Database session dependency.

    Returns:
        CardResponse: The updated card details.

    Raises:
        HTTPException: If the card is not found or there's a database error.
    """
    try:
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if not db_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with id {card_id} not found"
            )

        # Update fields
        for key, value in card.dict(exclude_unset=True).items():
            if key != "id":  # Don't update the ID
                setattr(db_card, key, value)

        db.commit()
        db.refresh(db_card)
        return convert_card_to_response(db_card)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cards"])
def delete_card(card_id: str, db: Session = Depends(get_db)):
    """
    Delete a card by its ID.

    Args:
        card_id (str): The ID of the card to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the card is not found or there's a database error.
    """
    try:
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if not db_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with id {card_id} not found"
            )

        db.delete(db_card)
        db.commit()
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e

# -----------------------------------------
# User Resources Endpoints
# -----------------------------------------

@app.post(
    "/api/users/{user_id}/resources",
    response_model=UserResourcesResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User Resources"]
)
def create_user_resources(
    user_id: str,
    resources: UserResourcesCreate,
    db: Session = Depends(get_db)
):
    """
    Create initial resources for a user.

    Args:
        user_id (str): The user identifier
        resources (UserResourcesCreate): Initial resource values
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The created user resources

    Raises:
        HTTPException: If resources already exist or database error occurs
    """
    try:
        # Check if resources already exist
        existing = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resources already exist for user {user_id}"
            )

        db_resources = UserResources(user_id=user_id, **resources.dict(exclude={'user_id'}))
        db.add(db_resources)
        db.commit()
        db.refresh(db_resources)
        return db_resources
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User resources already exist: {str(e)}"
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@app.get(
    "/api/users/{user_id}/resources",
    response_model=UserResourcesResponse,
    tags=["User Resources"]
)
def get_user_resources(user_id: str, db: Session = Depends(get_db)):
    """
    Get user's current resources.

    Args:
        user_id (str): The user identifier
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The user's current resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            # Auto-create default resources for new users
            resources = UserResources(user_id=user_id)
            db.add(resources)
            db.commit()
            db.refresh(resources)
        return resources
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@app.put(
    "/api/users/{user_id}/resources",
    response_model=UserResourcesResponse,
    tags=["User Resources"]
)
def update_user_resources(
    user_id: str,
    updates: UserResourcesUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user's resources.

    Args:
        user_id (str): The user identifier
        updates (UserResourcesUpdate): Resource updates
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The updated resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resources not found for user {user_id}"
            )

        # Update fields
        for key, value in updates.dict(exclude_unset=True).items():
            if value is not None:
                setattr(resources, key, value)

        db.commit()
        db.refresh(resources)
        return resources
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@app.patch(
    "/api/users/{user_id}/resources/wildcards",
    response_model=UserResourcesResponse,
    tags=["User Resources"]
)
def update_wildcards(
    user_id: str,
    wildcard: WildcardUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific wildcard amount.

    Args:
        user_id (str): The user identifier
        wildcard (WildcardUpdate): Wildcard rarity and new amount
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The updated resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resources not found for user {user_id}"
            )

        resources.update_wildcards(wildcard.rarity.value, wildcard.amount)
        db.commit()
        db.refresh(resources)
        return resources
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@app.patch(
    "/api/users/{user_id}/resources/currency",
    response_model=UserResourcesResponse,
    tags=["User Resources"]
)
def update_currency(
    user_id: str,
    currency: CurrencyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user's currency (gold and/or gems).

    Args:
        user_id (str): The user identifier
        currency (CurrencyUpdate): Currency updates
        db (Session): Database session dependency

    Returns:
        UserResourcesResponse: The updated resources

    Raises:
        HTTPException: If resources not found or database error occurs
    """
    try:
        resources = db.query(UserResources).filter(
            UserResources.user_id == user_id
        ).first()
        if not resources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resources not found for user {user_id}"
            )

        resources.update_currency(gold=currency.gold, gems=currency.gems)
        db.commit()
        db.refresh(resources)
        return resources
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


# -----------------------------------------
# Deck Generation & Building Endpoints
# -----------------------------------------

@app.post(
    "/api/decks/generate",
    response_model=DeckResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Deck Building"]
)
async def generate_deck(requirements: DeckRequirements, db: Session = Depends(get_db)):
    """
    Generate a new deck using AI agents based on specified requirements.

    This endpoint uses the multi-agent workflow to create an optimized deck
    that meets the specified requirements.

    Args:
        requirements (DeckRequirements): Deck building requirements and constraints.
        db (Session): Database session dependency.

    Returns:
        DeckResponse: The generated deck details.

    Raises:
        HTTPException: If there's an error during deck generation or database operations.
    """
    try:
        # Initialize LLM
        llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            streaming=False
        )

        # Initialize database handler
        card_db = CardDatabase(settings.get_database_url)

        # Create initial state
        initial_state = AgentState(
            requirements=requirements,
            messages=[HumanMessage(content=json.dumps(requirements.dict()))],
            current_agent="strategy"
        )

        # Create and run workflow
        workflow = create_deck_building_graph(llm, card_db)
        compiled_workflow = workflow.compile()
        final_state = await compiled_workflow.ainvoke(initial_state)

        # Get the generated deck
        generated_deck = final_state.get("deck")
        if not generated_deck:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate deck"
            )

        # Save the deck to database
        db_deck = Deck(
            name=generated_deck.name,
            format=generated_deck.format,
            description=generated_deck.description,
            mainboard=generated_deck.mainboard or {},
            sideboard=generated_deck.sideboard or {},
            colors=generated_deck.colors or [],
            strategy_tags=generated_deck.strategy_tags or []
        )
        db.add(db_deck)
        db.commit()
        db.refresh(db_deck)

        return convert_deck_to_response(db_deck)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating deck: {str(e)}"
        ) from e

@app.post("/api/decks/build", tags=["Deck Building"])
async def build_deck_workflow(requirements: DeckRequirements):
    """
    Start a deck building workflow and return the deck building process status.

    This endpoint initiates the multi-agent deck building workflow without
    saving to the database. Use this for interactive deck building.

    Args:
        requirements (DeckRequirements): Deck building requirements and constraints.

    Returns:
        dict: The workflow status and generated deck data.

    Raises:
        HTTPException: If there's an error during deck building.
    """
    try:
        # Initialize LLM
        llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            streaming=False
        )

        # Initialize database handler
        card_db = CardDatabase(settings.get_database_url)

        # Create initial state
        initial_state = AgentState(
            requirements=requirements,
            messages=[HumanMessage(content=json.dumps(requirements.dict()))],
            current_agent="strategy"
        )

        # Create and run workflow
        workflow = create_deck_building_graph(llm, card_db)
        compiled_workflow = workflow.compile()
        final_state = await compiled_workflow.ainvoke(initial_state)

        # Get the generated deck
        generated_deck = final_state.get("deck")
        if not generated_deck:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to build deck"
            )

        return {
            "status": "completed",
            "deck": generated_deck.dict() if hasattr(generated_deck, "dict") else generated_deck,
            "iterations": final_state.get("iteration", 0),
            "messages": [msg.content for msg in final_state.get("messages", [])]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building deck: {str(e)}"
        ) from e

# -----------------------------------------
# WebSocket Endpoint for Streaming
# -----------------------------------------

class ConnectionManager:
    """Manages WebSocket connections for streaming deck building updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and add it to active connections."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from active connections."""
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast a message to all active WebSocket connections."""
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/deck-builder")
async def websocket_deck_builder(websocket: WebSocket):
    """
    WebSocket endpoint for streaming deck building updates.

    Accepts deck requirements as JSON and streams the deck building process
    in real-time, including agent decisions, card selections, and optimizations.

    Usage:
        1. Connect to ws://host:port/ws/deck-builder
        2. Send deck requirements as JSON
        3. Receive streaming updates as the deck is built
    """
    await manager.connect(websocket)
    try:
        # Wait for requirements
        data = await websocket.receive_text()
        requirements_dict = json.loads(data)
        requirements = DeckRequirements(**requirements_dict)

        await manager.send_message(
            json.dumps({"status": "started", "message": "Deck building initiated"}),
            websocket
        )

        # Initialize LLM with streaming
        llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            streaming=True
        )

        # Initialize database handler
        card_db = CardDatabase(settings.get_database_url)

        # Create initial state
        initial_state = AgentState(
            requirements=requirements,
            messages=[HumanMessage(content=json.dumps(requirements.dict()))],
            current_agent="strategy"
        )

        # Stream updates during workflow
        await manager.send_message(
            json.dumps({
                "status": "processing",
                "agent": "strategy",
                "message": "Analyzing deck strategy"
            }),
            websocket
        )

        # Create and run workflow
        workflow = create_deck_building_graph(llm, card_db)
        compiled_workflow = workflow.compile()

        # Stream workflow execution
        async for event in compiled_workflow.astream(initial_state):
            # Send updates for each agent step
            for node_name, node_output in event.items():
                await manager.send_message(
                    json.dumps({
                        "status": "processing",
                        "agent": node_name,
                        "message": f"Agent {node_name} completed",
                        "data": str(node_output.get("current_agent", ""))
                    }),
                    websocket
                )

        # Get final state
        final_state = await compiled_workflow.ainvoke(initial_state)
        generated_deck = final_state.get("deck")

        if generated_deck:
            deck_data = (
                generated_deck.dict()
                if hasattr(generated_deck, "dict")
                else generated_deck
            )
            await manager.send_message(
                json.dumps({
                    "status": "completed",
                    "message": "Deck building completed",
                    "deck": deck_data
                }),
                websocket
            )
        else:
            await manager.send_message(
                json.dumps({"status": "error", "message": "Failed to generate deck"}),
                websocket
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Catch all exceptions in WebSocket handler to prevent server crash
        await manager.send_message(
            json.dumps({"status": "error", "message": f"Error: {str(e)}"}),
            websocket
        )
        manager.disconnect(websocket)

# -----------------------------------------
# Run the app
# -----------------------------------------

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
