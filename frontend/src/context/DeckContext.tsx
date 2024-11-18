import React, { createContext, useState, useContext, useEffect } from 'react';
import { Deck, Card } from '../types';

interface DeckContextType {
  currentDeck: Deck | null;
  savedDecks: Deck[];
  addCardToDeck: (card: Card) => void;
  removeCardFromDeck: (cardId: string) => void;
  setCurrentDeck: (deck: Deck | null) => void;
  saveDeck: (deck: Deck) => void;
  loadDeck: (deckId: string) => void;
  deleteDeck: (deckId: string) => void;
}

const DeckContext = createContext<DeckContextType | undefined>(undefined);

const SAVED_DECKS_KEY = 'mtga_saved_decks';
const CURRENT_DECK_KEY = 'mtga_current_deck';

export const DeckProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [currentDeck, setCurrentDeck] = useState<Deck | null>(() => {
    const saved = localStorage.getItem(CURRENT_DECK_KEY);
    return saved ? JSON.parse(saved) : null;
  });

  const [savedDecks, setSavedDecks] = useState<Deck[]>(() => {
    const saved = localStorage.getItem(SAVED_DECKS_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    if (currentDeck) {
      localStorage.setItem(CURRENT_DECK_KEY, JSON.stringify(currentDeck));
    }
  }, [currentDeck]);

  useEffect(() => {
    localStorage.setItem(SAVED_DECKS_KEY, JSON.stringify(savedDecks));
  }, [savedDecks]);

  const addCardToDeck = (card: Card) => {
    if (!currentDeck) {
      setCurrentDeck({
        id: Date.now().toString(),
        name: 'New Deck',
        format: 'Standard',
        cards: [{ card, quantity: 1 }]
      });
      return;
    }

    const existingCardIndex = currentDeck.cards.findIndex(c => c.card.id === card.id);
    
    if (existingCardIndex > -1) {
      const updatedCards = [...currentDeck.cards];
      updatedCards[existingCardIndex].quantity += 1;
      setCurrentDeck({ ...currentDeck, cards: updatedCards });
    } else {
      setCurrentDeck({
        ...currentDeck,
        cards: [...currentDeck.cards, { card, quantity: 1 }]
      });
    }
  };

  const removeCardFromDeck = (cardId: string) => {
    if (!currentDeck) return;

    const updatedCards = currentDeck.cards
      .map(item => 
        item.card.id === cardId 
          ? { ...item, quantity: Math.max(0, item.quantity - 1) }
          : item
      )
      .filter(item => item.quantity > 0);

    setCurrentDeck({ ...currentDeck, cards: updatedCards });
  };

  const saveDeck = (deck: Deck) => {
    const deckToSave = { ...deck, id: deck.id || Date.now().toString() };
    setSavedDecks(prevDecks => {
      const existingIndex = prevDecks.findIndex(d => d.id === deckToSave.id);
      if (existingIndex >= 0) {
        const updatedDecks = [...prevDecks];
        updatedDecks[existingIndex] = deckToSave;
        return updatedDecks;
      }
      return [...prevDecks, deckToSave];
    });
  };

  const loadDeck = (deckId: string) => {
    const deck = savedDecks.find(d => d.id === deckId);
    if (deck) {
      setCurrentDeck(deck);
    }
  };

  const deleteDeck = (deckId: string) => {
    setSavedDecks(prevDecks => prevDecks.filter(d => d.id !== deckId));
    if (currentDeck?.id === deckId) {
      setCurrentDeck(null);
    }
  };

  return (
    <DeckContext.Provider value={{ 
      currentDeck, 
      savedDecks,
      addCardToDeck, 
      removeCardFromDeck,
      setCurrentDeck,  
      saveDeck,
      loadDeck,
      deleteDeck
    }}>
      {children}
    </DeckContext.Provider>
  );
};

export const useDeck = () => {
  const context = useContext(DeckContext);
  if (context === undefined) {
    throw new Error('useDeck must be used within a DeckProvider');
  }
  return context;
};