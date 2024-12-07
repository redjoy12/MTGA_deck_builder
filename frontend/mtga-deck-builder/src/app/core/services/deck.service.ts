import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';

// Import interfaces
import { Deck } from '../../models/deck.interface';
import { DeckRequirements } from '../../models/deck-requirements.interface';
import { Card } from '../../models/card.interface';

@Injectable({
  providedIn: 'root'
})
export class DeckService {
  // Base API URL - replace with your actual backend URL
  private apiUrl = 'http://localhost:8000/api/decks';

  constructor(private http: HttpClient) {}

  // Create a new deck
  createDeck(deck: Deck): Observable<Deck> {
    return this.http.post<Deck>(`${this.apiUrl}`, deck)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Generate a deck based on requirements
  generateDeck(requirements: DeckRequirements): Observable<Deck> {
    return this.http.post<Deck>(`${this.apiUrl}/generate`, requirements)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get a specific deck by ID
  getDeckById(deckId: string): Observable<Deck> {
    return this.http.get<Deck>(`${this.apiUrl}/${deckId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Update an existing deck
  updateDeck(deck: Deck): Observable<Deck> {
    if (!deck.id) {
      throw new Error('Deck ID is required for updating');
    }
    return this.http.put<Deck>(`${this.apiUrl}/${deck.id}`, deck)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Delete a deck
  deleteDeck(deckId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${deckId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get user's deck history
  getDeckHistory(): Observable<Deck[]> {
    return this.http.get<Deck[]>(`${this.apiUrl}/history`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get decks by format and strategy
  searchDecks(format?: string, strategy?: string): Observable<Deck[]> {
    let params = new HttpParams();

    if (format) {
      params = params.set('format', format);
    }

    if (strategy) {
      params = params.set('strategy', strategy);
    }

    return this.http.get<Deck[]>(`${this.apiUrl}/search`, { params })
      .pipe(
        catchError(this.handleError)
      );
  }

  // Add a card to a deck
  addCardToDeck(deckId: string, card: Card, quantity: number, sideboard: boolean = false): Observable<Deck> {
    return this.http.post<Deck>(`${this.apiUrl}/${deckId}/cards`, {
      card,
      quantity,
      sideboard
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Remove a card from a deck
  removeCardFromDeck(deckId: string, cardId: string, sideboard: boolean = false): Observable<Deck> {
    return this.http.delete<Deck>(`${this.apiUrl}/${deckId}/cards/${cardId}`, {
      params: new HttpParams().set('sideboard', sideboard.toString())
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Private error handler
  private handleError(error: any): Observable<never> {
    console.error('An error occurred:', error);
    throw error;
  }
}