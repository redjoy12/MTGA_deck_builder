import { ActionReducerMap } from '@ngrx/store';
import { DeckState, deckReducer } from './deck';
import { CardState, cardReducer } from './card';

/**
 * Root application state interface
 */
export interface AppState {
  deck: DeckState;
  card: CardState;
}

/**
 * Root reducers map
 */
export const reducers: ActionReducerMap<AppState> = {
  deck: deckReducer,
  card: cardReducer
};

// Re-export state slices for convenience
export * from './deck';
export * from './card';
