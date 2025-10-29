import { createAction, props } from '@ngrx/store';
import { Deck } from '../../models/deck.interface';
import { DeckRequirements } from '../../models/deck-requirements.interface';
import { Card } from '../../models/card.interface';

// Load Deck History
export const loadDeckHistory = createAction('[Deck] Load Deck History');

export const loadDeckHistorySuccess = createAction(
  '[Deck] Load Deck History Success',
  props<{ decks: Deck[] }>()
);

export const loadDeckHistoryFailure = createAction(
  '[Deck] Load Deck History Failure',
  props<{ error: string }>()
);

// Load Deck By ID
export const loadDeckById = createAction(
  '[Deck] Load Deck By ID',
  props<{ deckId: string }>()
);

export const loadDeckByIdSuccess = createAction(
  '[Deck] Load Deck By ID Success',
  props<{ deck: Deck }>()
);

export const loadDeckByIdFailure = createAction(
  '[Deck] Load Deck By ID Failure',
  props<{ error: string }>()
);

// Create Deck
export const createDeck = createAction(
  '[Deck] Create Deck',
  props<{ deck: Deck }>()
);

export const createDeckSuccess = createAction(
  '[Deck] Create Deck Success',
  props<{ deck: Deck }>()
);

export const createDeckFailure = createAction(
  '[Deck] Create Deck Failure',
  props<{ error: string }>()
);

// Generate Deck
export const generateDeck = createAction(
  '[Deck] Generate Deck',
  props<{ requirements: DeckRequirements }>()
);

export const generateDeckSuccess = createAction(
  '[Deck] Generate Deck Success',
  props<{ deck: Deck }>()
);

export const generateDeckFailure = createAction(
  '[Deck] Generate Deck Failure',
  props<{ error: string }>()
);

// Update Deck
export const updateDeck = createAction(
  '[Deck] Update Deck',
  props<{ deck: Deck }>()
);

export const updateDeckSuccess = createAction(
  '[Deck] Update Deck Success',
  props<{ deck: Deck }>()
);

export const updateDeckFailure = createAction(
  '[Deck] Update Deck Failure',
  props<{ error: string }>()
);

// Delete Deck
export const deleteDeck = createAction(
  '[Deck] Delete Deck',
  props<{ deckId: string }>()
);

export const deleteDeckSuccess = createAction(
  '[Deck] Delete Deck Success',
  props<{ deckId: string }>()
);

export const deleteDeckFailure = createAction(
  '[Deck] Delete Deck Failure',
  props<{ error: string }>()
);

// Search Decks
export const searchDecks = createAction(
  '[Deck] Search Decks',
  props<{ format?: string; strategy?: string }>()
);

export const searchDecksSuccess = createAction(
  '[Deck] Search Decks Success',
  props<{ decks: Deck[] }>()
);

export const searchDecksFailure = createAction(
  '[Deck] Search Decks Failure',
  props<{ error: string }>()
);

// Add Card to Deck
export const addCardToDeck = createAction(
  '[Deck] Add Card to Deck',
  props<{ deckId: string; card: Card; quantity: number; sideboard?: boolean }>()
);

export const addCardToDeckSuccess = createAction(
  '[Deck] Add Card to Deck Success',
  props<{ deck: Deck }>()
);

export const addCardToDeckFailure = createAction(
  '[Deck] Add Card to Deck Failure',
  props<{ error: string }>()
);

// Remove Card from Deck
export const removeCardFromDeck = createAction(
  '[Deck] Remove Card from Deck',
  props<{ deckId: string; cardId: string; sideboard?: boolean }>()
);

export const removeCardFromDeckSuccess = createAction(
  '[Deck] Remove Card from Deck Success',
  props<{ deck: Deck }>()
);

export const removeCardFromDeckFailure = createAction(
  '[Deck] Remove Card from Deck Failure',
  props<{ error: string }>()
);

// Select Deck
export const selectDeck = createAction(
  '[Deck] Select Deck',
  props<{ deck: Deck | null }>()
);

// Clear Error
export const clearDeckError = createAction('[Deck] Clear Error');
