import { Card } from '../../models/card.interface';

/**
 * Card state interface
 */
export interface CardState {
  // All cards (from search or suggestions)
  cards: Card[];

  // Selected card for preview/details
  selectedCard: Card | null;

  // Card suggestions based on deck requirements
  suggestions: Card[];

  // Loading states
  loading: boolean;
  loadingSuggestions: boolean;

  // Error handling
  error: string | null;

  // Last search parameters
  lastSearchParams: {
    searchTerm?: string;
    colors?: string[];
    manaCost?: number;
    type?: string;
    set?: string;
  } | null;

  // Last updated timestamp
  lastUpdated: number | null;
}

/**
 * Initial state for card slice
 */
export const initialCardState: CardState = {
  cards: [],
  selectedCard: null,
  suggestions: [],
  loading: false,
  loadingSuggestions: false,
  error: null,
  lastSearchParams: null,
  lastUpdated: null
};
