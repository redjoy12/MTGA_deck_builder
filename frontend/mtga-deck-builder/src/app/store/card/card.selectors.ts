import { createFeatureSelector, createSelector } from '@ngrx/store';
import { CardState } from './card.state';

// Feature selector
export const selectCardState = createFeatureSelector<CardState>('card');

// Basic selectors
export const selectAllCards = createSelector(
  selectCardState,
  (state: CardState) => state.cards
);

export const selectSelectedCard = createSelector(
  selectCardState,
  (state: CardState) => state.selectedCard
);

export const selectCardSuggestions = createSelector(
  selectCardState,
  (state: CardState) => state.suggestions
);

export const selectCardLoading = createSelector(
  selectCardState,
  (state: CardState) => state.loading
);

export const selectCardSuggestionsLoading = createSelector(
  selectCardState,
  (state: CardState) => state.loadingSuggestions
);

export const selectCardError = createSelector(
  selectCardState,
  (state: CardState) => state.error
);

export const selectLastSearchParams = createSelector(
  selectCardState,
  (state: CardState) => state.lastSearchParams
);

export const selectCardLastUpdated = createSelector(
  selectCardState,
  (state: CardState) => state.lastUpdated
);

// Composite selectors
export const selectIsAnyCardOperation = createSelector(
  selectCardLoading,
  selectCardSuggestionsLoading,
  (loading, loadingSuggestions) => loading || loadingSuggestions
);

// Select cards by color
export const selectCardsByColor = (color: string) => createSelector(
  selectAllCards,
  (cards) => cards.filter(card =>
    card.color_identity?.includes(color) || card.colors?.includes(color)
  )
);

// Select cards by type
export const selectCardsByType = (type: string) => createSelector(
  selectAllCards,
  (cards) => cards.filter(card =>
    card.type_line?.toLowerCase().includes(type.toLowerCase()) ||
    card.type?.toLowerCase().includes(type.toLowerCase())
  )
);

// Select cards by rarity
export const selectCardsByRarity = (rarity: string) => createSelector(
  selectAllCards,
  (cards) => cards.filter(card =>
    card.rarity?.toLowerCase() === rarity.toLowerCase()
  )
);

// Select cards by CMC range
export const selectCardsByCMCRange = (minCMC: number, maxCMC: number) => createSelector(
  selectAllCards,
  (cards) => cards.filter(card =>
    card.cmc !== undefined && card.cmc >= minCMC && card.cmc <= maxCMC
  )
);

// Count total cards
export const selectTotalCards = createSelector(
  selectAllCards,
  (cards) => cards.length
);

// Count total suggestions
export const selectTotalSuggestions = createSelector(
  selectCardSuggestions,
  (suggestions) => suggestions.length
);
