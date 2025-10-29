import { createReducer, on } from '@ngrx/store';
import { CardState, initialCardState } from './card.state';
import * as CardActions from './card.actions';

export const cardReducer = createReducer(
  initialCardState,

  // Search Cards
  on(CardActions.searchCards, (state, params): CardState => ({
    ...state,
    loading: true,
    error: null,
    lastSearchParams: {
      searchTerm: params.searchTerm,
      colors: params.colors,
      manaCost: params.manaCost,
      type: params.type,
      set: params.set
    }
  })),

  on(CardActions.searchCardsSuccess, (state, { cards }): CardState => ({
    ...state,
    cards,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(CardActions.searchCardsFailure, (state, { error }): CardState => ({
    ...state,
    loading: false,
    error
  })),

  // Load Card By ID
  on(CardActions.loadCardById, (state): CardState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(CardActions.loadCardByIdSuccess, (state, { card }): CardState => ({
    ...state,
    selectedCard: card,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(CardActions.loadCardByIdFailure, (state, { error }): CardState => ({
    ...state,
    loading: false,
    error
  })),

  // Load Card Suggestions
  on(CardActions.loadCardSuggestions, (state): CardState => ({
    ...state,
    loadingSuggestions: true,
    error: null
  })),

  on(CardActions.loadCardSuggestionsSuccess, (state, { suggestions }): CardState => ({
    ...state,
    suggestions,
    loadingSuggestions: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(CardActions.loadCardSuggestionsFailure, (state, { error }): CardState => ({
    ...state,
    loadingSuggestions: false,
    error
  })),

  // Load Card Suggestions By Requirements
  on(CardActions.loadCardSuggestionsByRequirements, (state): CardState => ({
    ...state,
    loadingSuggestions: true,
    error: null
  })),

  on(CardActions.loadCardSuggestionsByRequirementsSuccess, (state, { suggestions }): CardState => ({
    ...state,
    suggestions,
    loadingSuggestions: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(CardActions.loadCardSuggestionsByRequirementsFailure, (state, { error }): CardState => ({
    ...state,
    loadingSuggestions: false,
    error
  })),

  // Load Cards By Set
  on(CardActions.loadCardsBySet, (state): CardState => ({
    ...state,
    loading: true,
    error: null
  })),

  on(CardActions.loadCardsBySetSuccess, (state, { cards }): CardState => ({
    ...state,
    cards,
    loading: false,
    error: null,
    lastUpdated: Date.now()
  })),

  on(CardActions.loadCardsBySetFailure, (state, { error }): CardState => ({
    ...state,
    loading: false,
    error
  })),

  // Select Card
  on(CardActions.selectCard, (state, { card }): CardState => ({
    ...state,
    selectedCard: card
  })),

  // Clear Cards
  on(CardActions.clearCards, (state): CardState => ({
    ...state,
    cards: [],
    lastSearchParams: null
  })),

  // Clear Suggestions
  on(CardActions.clearSuggestions, (state): CardState => ({
    ...state,
    suggestions: []
  })),

  // Clear Error
  on(CardActions.clearCardError, (state): CardState => ({
    ...state,
    error: null
  }))
);
