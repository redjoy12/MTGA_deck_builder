import { createAction, props } from '@ngrx/store';
import { Card } from '../../models/card.interface';
import { DeckRequirements } from '../../models/deck-requirements.interface';

// Search Cards
export const searchCards = createAction(
  '[Card] Search Cards',
  props<{
    searchTerm?: string;
    colors?: string[];
    manaCost?: number;
    type?: string;
    set?: string;
  }>()
);

export const searchCardsSuccess = createAction(
  '[Card] Search Cards Success',
  props<{ cards: Card[] }>()
);

export const searchCardsFailure = createAction(
  '[Card] Search Cards Failure',
  props<{ error: string }>()
);

// Load Card By ID
export const loadCardById = createAction(
  '[Card] Load Card By ID',
  props<{ cardId: string }>()
);

export const loadCardByIdSuccess = createAction(
  '[Card] Load Card By ID Success',
  props<{ card: Card }>()
);

export const loadCardByIdFailure = createAction(
  '[Card] Load Card By ID Failure',
  props<{ error: string }>()
);

// Get Card Suggestions
export const loadCardSuggestions = createAction(
  '[Card] Load Card Suggestions',
  props<{ colors: string[]; strategy: string }>()
);

export const loadCardSuggestionsSuccess = createAction(
  '[Card] Load Card Suggestions Success',
  props<{ suggestions: Card[] }>()
);

export const loadCardSuggestionsFailure = createAction(
  '[Card] Load Card Suggestions Failure',
  props<{ error: string }>()
);

// Get Card Suggestions By Requirements
export const loadCardSuggestionsByRequirements = createAction(
  '[Card] Load Card Suggestions By Requirements',
  props<{ requirements: DeckRequirements }>()
);

export const loadCardSuggestionsByRequirementsSuccess = createAction(
  '[Card] Load Card Suggestions By Requirements Success',
  props<{ suggestions: Card[] }>()
);

export const loadCardSuggestionsByRequirementsFailure = createAction(
  '[Card] Load Card Suggestions By Requirements Failure',
  props<{ error: string }>()
);

// Get Cards By Set
export const loadCardsBySet = createAction(
  '[Card] Load Cards By Set',
  props<{ setCode: string }>()
);

export const loadCardsBySetSuccess = createAction(
  '[Card] Load Cards By Set Success',
  props<{ cards: Card[] }>()
);

export const loadCardsBySetFailure = createAction(
  '[Card] Load Cards By Set Failure',
  props<{ error: string }>()
);

// Select Card
export const selectCard = createAction(
  '[Card] Select Card',
  props<{ card: Card | null }>()
);

// Clear Cards
export const clearCards = createAction('[Card] Clear Cards');

// Clear Suggestions
export const clearSuggestions = createAction('[Card] Clear Suggestions');

// Clear Error
export const clearCardError = createAction('[Card] Clear Error');
