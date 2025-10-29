import { Deck } from '../../models/deck.interface';

/**
 * Deck state interface
 */
export interface DeckState {
  // All decks (e.g., from history or search)
  decks: Deck[];

  // Currently selected/active deck
  selectedDeck: Deck | null;

  // Loading states
  loading: boolean;
  creating: boolean;
  generating: boolean;

  // Error handling
  error: string | null;

  // Last updated timestamp
  lastUpdated: number | null;
}

/**
 * Initial state for deck slice
 */
export const initialDeckState: DeckState = {
  decks: [],
  selectedDeck: null,
  loading: false,
  creating: false,
  generating: false,
  error: null,
  lastUpdated: null
};
