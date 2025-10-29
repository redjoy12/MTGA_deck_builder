import { createFeatureSelector, createSelector } from '@ngrx/store';
import { DeckState } from './deck.state';

// Feature selector
export const selectDeckState = createFeatureSelector<DeckState>('deck');

// Basic selectors
export const selectAllDecks = createSelector(
  selectDeckState,
  (state: DeckState) => state.decks
);

export const selectSelectedDeck = createSelector(
  selectDeckState,
  (state: DeckState) => state.selectedDeck
);

export const selectDeckLoading = createSelector(
  selectDeckState,
  (state: DeckState) => state.loading
);

export const selectDeckCreating = createSelector(
  selectDeckState,
  (state: DeckState) => state.creating
);

export const selectDeckGenerating = createSelector(
  selectDeckState,
  (state: DeckState) => state.generating
);

export const selectDeckError = createSelector(
  selectDeckState,
  (state: DeckState) => state.error
);

export const selectDeckLastUpdated = createSelector(
  selectDeckState,
  (state: DeckState) => state.lastUpdated
);

// Composite selectors
export const selectIsAnyDeckOperation = createSelector(
  selectDeckLoading,
  selectDeckCreating,
  selectDeckGenerating,
  (loading, creating, generating) => loading || creating || generating
);

// Select deck by ID
export const selectDeckById = (deckId: string) => createSelector(
  selectAllDecks,
  (decks) => decks.find(deck => deck.id?.toString() === deckId)
);

// Select decks by format
export const selectDecksByFormat = (format: string) => createSelector(
  selectAllDecks,
  (decks) => decks.filter(deck => deck.format === format)
);

// Select decks by color
export const selectDecksByColor = (color: string) => createSelector(
  selectAllDecks,
  (decks) => decks.filter(deck => deck.colors.includes(color))
);

// Count total decks
export const selectTotalDecks = createSelector(
  selectAllDecks,
  (decks) => decks.length
);
