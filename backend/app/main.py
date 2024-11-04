# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.core.database import get_db
from app.models.card import Deck, Card
from app.models.schemas import DeckCreate, DeckResponse, CardCreate, CardResponse

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
@app.get("/")
async def root():
    return {"message": "Welcome to MTGA AI Deck Builder API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# -----------------------------------------
# Deck Endpoints
# -----------------------------------------

@app.post("/decks", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    db_deck = Deck(**deck.dict())
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

@app.get("/decks/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Include accessor methods in response
    return DeckResponse(
        **db_deck.__dict__,
        total_card_count=db_deck.get_total_card_count(),
        color_distribution=db_deck.get_color_distribution()
    )

@app.get("/decks", response_model=list[DeckResponse])
def list_decks(db: Session = Depends(get_db)):
    return db.query(Deck).all()

# -----------------------------------------
# Card Endpoints
# -----------------------------------------

@app.post("/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    db_card = Card(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@app.get("/cards/{card_id}", response_model=CardResponse)
def get_card(card_id: str, db: Session = Depends(get_db)):
    db_card = db.query(Card).filter(Card.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    return db_card

@app.get("/cards", response_model=list[CardResponse])
def list_cards(db: Session = Depends(get_db)):
    return db.query(Card).all()

# -----------------------------------------
# Run the app
# -----------------------------------------

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
