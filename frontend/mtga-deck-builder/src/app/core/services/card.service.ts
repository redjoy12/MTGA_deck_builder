import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';

// Import interfaces
import { Card } from '../../models/card.interface';
import { DeckRequirements } from '../../models/deck-requirements.interface';

@Injectable({
  providedIn: 'root'
})
export class CardService {
  // Base API URL - replace with your actual backend URL
  private apiUrl = 'http://localhost:8000/api/cards';

  constructor(private http: HttpClient) {}

  // Search cards with flexible parameters
  searchCards(params: {
    searchTerm?: string;
    colors?: string[];
    manaCost?: number;
    type?: string;
    set?: string;
  }): Observable<Card[]> {
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
        catchError(this.handleError)
      );
  }

  // Get a specific card by ID
  getCardById(cardId: string): Observable<Card> {
    return this.http.get<Card>(`${this.apiUrl}/${cardId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get card suggestions based on deck strategy
  getCardSuggestions(colors: string[], strategy: string): Observable<Card[]> {
    let params = new HttpParams()
      .set('colors', colors.join(','))
      .set('strategy', strategy);

    return this.http.get<Card[]>(`${this.apiUrl}/suggestions`, { params })
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get cards by set
  getCardsBySet(setCode: string): Observable<Card[]> {
    return this.http.get<Card[]>(`${this.apiUrl}/set/${setCode}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get card suggestions based on deck requirements
  getCardSuggestionsByRequirements(requirements: DeckRequirements): Observable<Card[]> {
    return this.http.post<Card[]>(`${this.apiUrl}/suggestions`, requirements)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Private error handler
  private handleError(error: any): Observable<never> {
    console.error('An error occurred:', error);
    throw error;
  }
}