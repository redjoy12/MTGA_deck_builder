# backend/app/main.py
import uvicorn
from app.core.database import get_db
from app.models.card import Card, Deck
from app.models.schemas import (CardCreate, CardResponse, DeckCreate, DeckResponse)
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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

@app.post("/decks", response_model=DeckResponse, status_code=status.HTTP_201_CREATED, tags=["Decks"])
def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    """
    Create a new deck with specified attributes.
    
    Args:
        deck (DeckCreate): A Pydantic model containing deck creation data.
        db (Session): Database session dependency.
    
    Returns:
        DeckResponse: The created deck details, including all attributes.
    """
    db_deck = Deck(**deck.dict())
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

@app.get("/decks/{deck_id}", response_model=DeckResponse, tags=["Decks"])
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a deck by its ID, including additional information such as total card count
    and color distribution.
    
    Args:
        deck_id (int): The ID of the deck to retrieve.
        db (Session): Database session dependency.
    
    Returns:
        DeckResponse: The deck details with total card count and color distribution.
    
    Raises:
        HTTPException: If the deck with the specified ID is not found.
    """
    db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return DeckResponse(
        **db_deck.__dict__,
        total_card_count=db_deck.get_total_card_count(),
        color_distribution=db_deck.get_color_distribution()
    )

@app.get("/decks", response_model=list[DeckResponse], tags=["Decks"])
def list_decks(db: Session = Depends(get_db)):
    """
    List all decks in the database.
    
    Args:
        db (Session): Database session dependency.
    
    Returns:
        list[DeckResponse]: A list of all decks.
    """
    return db.query(Deck).all()

# -----------------------------------------
# Card Endpoints
# -----------------------------------------

@app.post("/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED, tags=["Cards"])
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    """
    Create a new card with specified attributes.
    
    Args:
        card (CardCreate): A Pydantic model containing card creation data.
        db (Session): Database session dependency.
    
    Returns:
        CardResponse: The created card details, including all attributes.
    """
    db_card = Card(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

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
    db_card = db.query(Card).filter(Card.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    return db_card

@app.get("/cards", response_model=list[CardResponse], tags=["Cards"])
def list_cards(db: Session = Depends(get_db)):
    """
    List all cards in the database.
    
    Args:
        db (Session): Database session dependency.
    
    Returns:
        list[CardResponse]: A list of all cards.
    """
    return db.query(Card).all()

# -----------------------------------------
# Run the app
# -----------------------------------------

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
