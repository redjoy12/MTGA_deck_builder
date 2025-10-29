import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';
import { DeckService } from '../../core/services/deck.service';
import * as DeckActions from './deck.actions';

@Injectable()
export class DeckEffects {
  constructor(
    private actions$: Actions,
    private deckService: DeckService
  ) {}

  // Load Deck History
  loadDeckHistory$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.loadDeckHistory),
      switchMap(() =>
        this.deckService.getDeckHistory().pipe(
          map(decks => DeckActions.loadDeckHistorySuccess({ decks })),
          catchError(error =>
            of(DeckActions.loadDeckHistoryFailure({
              error: error?.message || 'Failed to load deck history'
            }))
          )
        )
      )
    )
  );

  // Load Deck By ID
  loadDeckById$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.loadDeckById),
      switchMap(({ deckId }) =>
        this.deckService.getDeckById(deckId).pipe(
          map(deck => DeckActions.loadDeckByIdSuccess({ deck })),
          catchError(error =>
            of(DeckActions.loadDeckByIdFailure({
              error: error?.message || 'Failed to load deck'
            }))
          )
        )
      )
    )
  );

  // Create Deck
  createDeck$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.createDeck),
      switchMap(({ deck }) =>
        this.deckService.createDeck(deck).pipe(
          map(createdDeck => DeckActions.createDeckSuccess({ deck: createdDeck })),
          catchError(error =>
            of(DeckActions.createDeckFailure({
              error: error?.message || 'Failed to create deck'
            }))
          )
        )
      )
    )
  );

  // Generate Deck
  generateDeck$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.generateDeck),
      switchMap(({ requirements }) =>
        this.deckService.generateDeck(requirements).pipe(
          map(deck => DeckActions.generateDeckSuccess({ deck })),
          catchError(error =>
            of(DeckActions.generateDeckFailure({
              error: error?.message || 'Failed to generate deck'
            }))
          )
        )
      )
    )
  );

  // Update Deck
  updateDeck$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.updateDeck),
      switchMap(({ deck }) =>
        this.deckService.updateDeck(deck).pipe(
          map(updatedDeck => DeckActions.updateDeckSuccess({ deck: updatedDeck })),
          catchError(error =>
            of(DeckActions.updateDeckFailure({
              error: error?.message || 'Failed to update deck'
            }))
          )
        )
      )
    )
  );

  // Delete Deck
  deleteDeck$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.deleteDeck),
      switchMap(({ deckId }) =>
        this.deckService.deleteDeck(deckId).pipe(
          map(() => DeckActions.deleteDeckSuccess({ deckId })),
          catchError(error =>
            of(DeckActions.deleteDeckFailure({
              error: error?.message || 'Failed to delete deck'
            }))
          )
        )
      )
    )
  );

  // Search Decks
  searchDecks$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.searchDecks),
      switchMap(({ format, strategy }) =>
        this.deckService.searchDecks(format, strategy).pipe(
          map(decks => DeckActions.searchDecksSuccess({ decks })),
          catchError(error =>
            of(DeckActions.searchDecksFailure({
              error: error?.message || 'Failed to search decks'
            }))
          )
        )
      )
    )
  );

  // Add Card to Deck
  addCardToDeck$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.addCardToDeck),
      switchMap(({ deckId, card, quantity, sideboard }) =>
        this.deckService.addCardToDeck(deckId, card, quantity, sideboard).pipe(
          map(deck => DeckActions.addCardToDeckSuccess({ deck })),
          catchError(error =>
            of(DeckActions.addCardToDeckFailure({
              error: error?.message || 'Failed to add card to deck'
            }))
          )
        )
      )
    )
  );

  // Remove Card from Deck
  removeCardFromDeck$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DeckActions.removeCardFromDeck),
      switchMap(({ deckId, cardId, sideboard }) =>
        this.deckService.removeCardFromDeck(deckId, cardId, sideboard).pipe(
          map(deck => DeckActions.removeCardFromDeckSuccess({ deck })),
          catchError(error =>
            of(DeckActions.removeCardFromDeckFailure({
              error: error?.message || 'Failed to remove card from deck'
            }))
          )
        )
      )
    )
  );
}
