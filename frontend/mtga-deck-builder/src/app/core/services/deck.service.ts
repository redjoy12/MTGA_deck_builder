import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

// Import interfaces
import { Deck } from '../../models/deck.interface';
import { DeckRequirements } from '../../models/deck-requirements.interface';
import { Card } from '../../models/card.interface';

// Import environment
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DeckService {
  // Base API URL from environment configuration
  private readonly apiUrl = `${environment.apiUrl}/decks`;

  constructor(private http: HttpClient) {}

  // Create a new deck
  createDeck(deck: Deck): Observable<Deck> {
    if (!deck) {
      return throwError(() => ({
        message: 'Deck data is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!deck.name || deck.name.trim() === '') {
      return throwError(() => ({
        message: 'Deck name is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.post<Deck>(`${this.apiUrl}`, deck)
      .pipe(
        retry(1), // Only retry once for POST requests
        catchError((error) => this.handleError(error, 'creating deck'))
      );
  }

  // Generate a deck based on requirements
  generateDeck(requirements: DeckRequirements): Observable<Deck> {
    if (!requirements) {
      return throwError(() => ({
        message: 'Deck requirements are required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!requirements.format) {
      return throwError(() => ({
        message: 'Deck format is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!requirements.colors || requirements.colors.length === 0) {
      return throwError(() => ({
        message: 'At least one color is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.post<Deck>(`${this.apiUrl}/generate`, requirements)
      .pipe(
        catchError((error) => this.handleError(error, 'generating deck'))
      );
  }

  // Get a specific deck by ID
  getDeckById(deckId: string): Observable<Deck> {
    if (!deckId || deckId.trim() === '') {
      return throwError(() => ({
        message: 'Deck ID is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.get<Deck>(`${this.apiUrl}/${deckId}`)
      .pipe(
        retry(2),
        catchError((error) => this.handleError(error, `fetching deck with ID: ${deckId}`))
      );
  }

  // Update an existing deck
  updateDeck(deck: Deck): Observable<Deck> {
    if (!deck) {
      return throwError(() => ({
        message: 'Deck data is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!deck.id) {
      return throwError(() => ({
        message: 'Deck ID is required for updating',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.put<Deck>(`${this.apiUrl}/${deck.id}`, deck)
      .pipe(
        retry(1),
        catchError((error) => this.handleError(error, `updating deck with ID: ${deck.id}`))
      );
  }

  // Delete a deck
  deleteDeck(deckId: string): Observable<void> {
    if (!deckId || deckId.trim() === '') {
      return throwError(() => ({
        message: 'Deck ID is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.delete<void>(`${this.apiUrl}/${deckId}`)
      .pipe(
        catchError((error) => this.handleError(error, `deleting deck with ID: ${deckId}`))
      );
  }

  // Get user's deck history
  getDeckHistory(): Observable<Deck[]> {
    return this.http.get<Deck[]>(`${this.apiUrl}/history`)
      .pipe(
        retry(2),
        catchError((error) => this.handleError(error, 'fetching deck history'))
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
        retry(2),
        catchError((error) => this.handleError(error, 'searching decks'))
      );
  }

  // Add a card to a deck
  addCardToDeck(deckId: string, card: Card, quantity: number, sideboard: boolean = false): Observable<Deck> {
    if (!deckId || deckId.trim() === '') {
      return throwError(() => ({
        message: 'Deck ID is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!card || !card.id) {
      return throwError(() => ({
        message: 'Valid card data is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (quantity <= 0) {
      return throwError(() => ({
        message: 'Quantity must be greater than 0',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.post<Deck>(`${this.apiUrl}/${deckId}/cards`, {
      card,
      quantity,
      sideboard
    }).pipe(
      retry(1),
      catchError((error) => this.handleError(error, `adding card to deck ${deckId}`))
    );
  }

  // Remove a card from a deck
  removeCardFromDeck(deckId: string, cardId: string, sideboard: boolean = false): Observable<Deck> {
    if (!deckId || deckId.trim() === '') {
      return throwError(() => ({
        message: 'Deck ID is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!cardId || cardId.trim() === '') {
      return throwError(() => ({
        message: 'Card ID is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.delete<Deck>(`${this.apiUrl}/${deckId}/cards/${cardId}`, {
      params: new HttpParams().set('sideboard', sideboard.toString())
    }).pipe(
      catchError((error) => this.handleError(error, `removing card from deck ${deckId}`))
    );
  }

  // Private error handler with context
  private handleError(error: HttpErrorResponse, context: string): Observable<never> {
    // Sanitize context to prevent format string vulnerabilities
    const sanitizedContext = this.sanitizeContext(context);
    console.error('Error: %s', sanitizedContext, error);

    // Let the interceptor handle the error, but add context
    return throwError(() => ({
      ...error,
      context: sanitizedContext,
      timestamp: new Date().toISOString()
    }));
  }

  /**
   * Sanitize context string to prevent format string vulnerabilities
   * Removes or escapes potentially dangerous characters
   */
  private sanitizeContext(text: string): string {
    if (!text) {
      return 'unknown operation';
    }

    // Convert to string and trim
    const str = String(text).trim();

    // Limit length to prevent DoS
    const maxLength = 150;
    const truncated = str.length > maxLength ? str.substring(0, maxLength) + '...' : str;

    // Remove control characters and other potentially dangerous characters
    // Allow only alphanumeric, spaces, and common punctuation
    const sanitized = truncated.replace(/[^\w\s\-':,./()]/g, '');

    return sanitized || 'unknown operation';
  }
}