import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import { CardService } from '../../core/services/card.service';
import * as CardActions from './card.actions';

@Injectable()
export class CardEffects {
  constructor(
    private actions$: Actions,
    private cardService: CardService
  ) {}

  // Search Cards
  searchCards$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CardActions.searchCards),
      switchMap(({ searchTerm, colors, manaCost, type, set }) =>
        this.cardService.searchCards({
          searchTerm,
          colors,
          manaCost,
          type,
          set
        }).pipe(
          map(cards => CardActions.searchCardsSuccess({ cards })),
          catchError(error =>
            of(CardActions.searchCardsFailure({
              error: error?.message || 'Failed to search cards'
            }))
          )
        )
      )
    )
  );

  // Load Card By ID
  loadCardById$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CardActions.loadCardById),
      switchMap(({ cardId }) =>
        this.cardService.getCardById(cardId).pipe(
          map(card => CardActions.loadCardByIdSuccess({ card })),
          catchError(error =>
            of(CardActions.loadCardByIdFailure({
              error: error?.message || 'Failed to load card'
            }))
          )
        )
      )
    )
  );

  // Load Card Suggestions
  loadCardSuggestions$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CardActions.loadCardSuggestions),
      switchMap(({ colors, strategy }) =>
        this.cardService.getCardSuggestions(colors, strategy).pipe(
          map(suggestions => CardActions.loadCardSuggestionsSuccess({ suggestions })),
          catchError(error =>
            of(CardActions.loadCardSuggestionsFailure({
              error: error?.message || 'Failed to load card suggestions'
            }))
          )
        )
      )
    )
  );

  // Load Card Suggestions By Requirements
  loadCardSuggestionsByRequirements$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CardActions.loadCardSuggestionsByRequirements),
      switchMap(({ requirements }) =>
        this.cardService.getCardSuggestionsByRequirements(requirements).pipe(
          map(suggestions => CardActions.loadCardSuggestionsByRequirementsSuccess({ suggestions })),
          catchError(error =>
            of(CardActions.loadCardSuggestionsByRequirementsFailure({
              error: error?.message || 'Failed to load card suggestions by requirements'
            }))
          )
        )
      )
    )
  );

  // Load Cards By Set
  loadCardsBySet$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CardActions.loadCardsBySet),
      switchMap(({ setCode }) =>
        this.cardService.getCardsBySet(setCode).pipe(
          map(cards => CardActions.loadCardsBySetSuccess({ cards })),
          catchError(error =>
            of(CardActions.loadCardsBySetFailure({
              error: error?.message || 'Failed to load cards by set'
            }))
          )
        )
      )
    )
  );
}
