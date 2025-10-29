import { createReducer, on } from '@ngrx/store';
import { DeckState, initialDeckState } from './deck.state';
import * as DeckActions from './deck.actions';

export const deckReducer = createReducer(
  initialDeckState,

  // Load Deck History
  on(DeckActions.loadDeckHistory, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.loadDeckHistorySuccess, (state, { decks }): DeckState => ({
    ...state,
    decks,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.loadDeckHistoryFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Load Deck By ID
  on(DeckActions.loadDeckById, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.loadDeckByIdSuccess, (state, { deck }): DeckState => ({
    ...state,
    selectedDeck: deck,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.loadDeckByIdFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Create Deck
  on(DeckActions.createDeck, (state): DeckState => ({
    ...state,
    creating: true,
    error: null
  })),

  on(DeckActions.createDeckSuccess, (state, { deck }): DeckState => ({
    ...state,
    decks: [...state.decks, deck],
    selectedDeck: deck,
    creating: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.createDeckFailure, (state, { error }): DeckState => ({
    ...state,
    creating: false,
    error
  })),

  // Generate Deck
  on(DeckActions.generateDeck, (state): DeckState => ({
    ...state,
    generating: true,
    error: null
  })),

  on(DeckActions.generateDeckSuccess, (state, { deck }): DeckState => ({
    ...state,
    decks: [...state.decks, deck],
    selectedDeck: deck,
    generating: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.generateDeckFailure, (state, { error }): DeckState => ({
    ...state,
    generating: false,
    error
  })),

  // Update Deck
  on(DeckActions.updateDeck, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.updateDeckSuccess, (state, { deck }): DeckState => ({
    ...state,
    decks: state.decks.map(d => d.id === deck.id ? deck : d),
    selectedDeck: state.selectedDeck?.id === deck.id ? deck : state.selectedDeck,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.updateDeckFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Delete Deck
  on(DeckActions.deleteDeck, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.deleteDeckSuccess, (state, { deckId }): DeckState => ({
    ...state,
    decks: state.decks.filter(d => d.id?.toString() !== deckId),
    selectedDeck: state.selectedDeck?.id?.toString() === deckId ? null : state.selectedDeck,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.deleteDeckFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Search Decks
  on(DeckActions.searchDecks, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.searchDecksSuccess, (state, { decks }): DeckState => ({
    ...state,
    decks,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.searchDecksFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Add Card to Deck
  on(DeckActions.addCardToDeck, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.addCardToDeckSuccess, (state, { deck }): DeckState => ({
    ...state,
    decks: state.decks.map(d => d.id === deck.id ? deck : d),
    selectedDeck: state.selectedDeck?.id === deck.id ? deck : state.selectedDeck,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.addCardToDeckFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Remove Card from Deck
  on(DeckActions.removeCardFromDeck, (state): DeckState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(DeckActions.removeCardFromDeckSuccess, (state, { deck }): DeckState => ({
    ...state,
    decks: state.decks.map(d => d.id === deck.id ? deck : d),
    selectedDeck: state.selectedDeck?.id === deck.id ? deck : state.selectedDeck,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(DeckActions.removeCardFromDeckFailure, (state, { error }): DeckState => ({
    ...state,
    loading: false,
    error
  })),

  // Select Deck
  on(DeckActions.selectDeck, (state, { deck }): DeckState => ({
    ...state,
    selectedDeck: deck
  })),

  // Clear Error
  on(DeckActions.clearDeckError, (state): DeckState => ({
    ...state,
    error: null
  }))
);
