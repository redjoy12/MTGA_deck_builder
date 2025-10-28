import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

// Import interfaces
import { Card } from '../../models/card.interface';
import { DeckRequirements } from '../../models/deck-requirements.interface';

// Import environment
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CardService {
  // Base API URL from environment configuration
  private readonly apiUrl = `${environment.apiUrl}/cards`;

  constructor(private http: HttpClient) {}

  // Search cards with flexible parameters
  searchCards(params: {
    searchTerm?: string;
    colors?: string[];
    manaCost?: number;
    type?: string;
    set?: string;
  }): Observable<Card[]> {
    // Validate input parameters
    if (!params || Object.keys(params).length === 0) {
      return throwError(() => ({
        message: 'Search parameters are required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    // Convert search parameters to HttpParams
    let httpParams = new HttpParams();

    if (params.searchTerm) {
      httpParams = httpParams.set('search', params.searchTerm);
    }

    if (params.colors && params.colors.length > 0) {
      httpParams = httpParams.set('colors', params.colors.join(','));
    }

    if (params.manaCost !== undefined && params.manaCost !== null) {
      httpParams = httpParams.set('maxCmc', params.manaCost.toString());
    }

    if (params.type) {
      httpParams = httpParams.set('type', params.type);
    }

    if (params.set) {
      httpParams = httpParams.set('set', params.set);
    }

    return this.http.get<Card[]>(`${this.apiUrl}/search`, { params: httpParams })
      .pipe(
        retry(2), // Retry failed requests up to 2 times
        catchError((error) => this.handleError(error, 'searching for cards'))
      );
  }

  // Get a specific card by ID
  getCardById(cardId: string): Observable<Card> {
    if (!cardId || cardId.trim() === '') {
      return throwError(() => ({
        message: 'Card ID is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.get<Card>(`${this.apiUrl}/${cardId}`)
      .pipe(
        retry(2),
        catchError((error) => this.handleError(error, `fetching card with ID: ${cardId}`))
      );
  }

  // Get card suggestions based on deck strategy
  getCardSuggestions(colors: string[], strategy: string): Observable<Card[]> {
    if (!colors || colors.length === 0) {
      return throwError(() => ({
        message: 'At least one color is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!strategy || strategy.trim() === '') {
      return throwError(() => ({
        message: 'Strategy is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    let params = new HttpParams()
      .set('colors', colors.join(','))
      .set('strategy', strategy);

    return this.http.get<Card[]>(`${this.apiUrl}/suggestions`, { params })
      .pipe(
        retry(2),
        catchError((error) => this.handleError(error, 'fetching card suggestions'))
      );
  }

  // Get cards by set
  getCardsBySet(setCode: string): Observable<Card[]> {
    if (!setCode || setCode.trim() === '') {
      return throwError(() => ({
        message: 'Set code is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.get<Card[]>(`${this.apiUrl}/set/${setCode}`)
      .pipe(
        retry(2),
        catchError((error) => this.handleError(error, `fetching cards from set: ${setCode}`))
      );
  }

  // Get card suggestions based on deck requirements
  getCardSuggestionsByRequirements(requirements: DeckRequirements): Observable<Card[]> {
    if (!requirements) {
      return throwError(() => ({
        message: 'Deck requirements are required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.post<Card[]>(`${this.apiUrl}/suggestions`, requirements)
      .pipe(
        retry(2),
        catchError((error) => this.handleError(error, 'fetching card suggestions by requirements'))
      );
  }

  // Private error handler with context
  private handleError(error: HttpErrorResponse, context: string): Observable<never> {
    // Sanitize context to prevent format string vulnerabilities
    const sanitizedContext = this.sanitizeContext(context);
    console.error('Error ' + sanitizedContext + ':', error);

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