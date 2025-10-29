import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, retry, tap } from 'rxjs/operators';

import { environment } from '../../../environments/environment';

/**
 * Enum for wildcard rarities
 */
export enum WildcardRarity {
  COMMON = 'common',
  UNCOMMON = 'uncommon',
  RARE = 'rare',
  MYTHIC = 'mythic'
}

/**
 * Interface for user resources response from backend
 */
export interface UserResources {
  id: number;
  user_id: string;
  common_wildcards: number;
  uncommon_wildcards: number;
  rare_wildcards: number;
  mythic_wildcards: number;
  gold: number;
  gems: number;
  created_at: string;
  updated_at: string;
}

/**
 * Interface for updating user resources
 */
export interface UserResourcesUpdate {
  common_wildcards?: number;
  uncommon_wildcards?: number;
  rare_wildcards?: number;
  mythic_wildcards?: number;
  gold?: number;
  gems?: number;
}

/**
 * Interface for wildcard update request
 */
export interface WildcardUpdate {
  rarity: WildcardRarity;
  amount: number;
}

/**
 * Interface for currency update request
 */
export interface CurrencyUpdate {
  gold?: number;
  gems?: number;
}

/**
 * Type-safe wildcard data structure for the component
 */
export interface WildcardData {
  common: { current: number; total: number };
  uncommon: { current: number; total: number };
  rare: { current: number; total: number };
  mythic: { current: number; total: number };
}

/**
 * Type for valid wildcard types
 */
export type WildcardType = keyof WildcardData;

/**
 * Service for managing user resources (wildcards and currency)
 */
@Injectable({
  providedIn: 'root'
})
export class UserResourcesService {
  private readonly apiUrl = `${environment.apiUrl}/users`;

  // Current resources state
  private resourcesSubject = new BehaviorSubject<UserResources | null>(null);
  public resources$ = this.resourcesSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Get current resources value
   */
  public get currentResourcesValue(): UserResources | null {
    return this.resourcesSubject.value;
  }

  /**
   * Get user resources from backend
   */
  getUserResources(userId: string): Observable<UserResources> {
    return this.http.get<UserResources>(`${this.apiUrl}/${userId}/resources`)
      .pipe(
        retry(1),
        tap(resources => {
          this.resourcesSubject.next(resources);
        }),
        catchError((error) => this.handleError(error, 'fetching user resources'))
      );
  }

  /**
   * Update user resources (full update)
   */
  updateUserResources(userId: string, updates: UserResourcesUpdate): Observable<UserResources> {
    return this.http.put<UserResources>(`${this.apiUrl}/${userId}/resources`, updates)
      .pipe(
        tap(resources => {
          this.resourcesSubject.next(resources);
        }),
        catchError((error) => this.handleError(error, 'updating user resources'))
      );
  }

  /**
   * Update a specific wildcard amount
   */
  updateWildcard(userId: string, rarity: WildcardRarity, amount: number): Observable<UserResources> {
    const update: WildcardUpdate = { rarity, amount };
    return this.http.patch<UserResources>(`${this.apiUrl}/${userId}/resources/wildcards`, update)
      .pipe(
        tap(resources => {
          this.resourcesSubject.next(resources);
        }),
        catchError((error) => this.handleError(error, 'updating wildcard'))
      );
  }

  /**
   * Update currency (gold and/or gems)
   */
  updateCurrency(userId: string, gold?: number, gems?: number): Observable<UserResources> {
    const update: CurrencyUpdate = { gold, gems };
    return this.http.patch<UserResources>(`${this.apiUrl}/${userId}/resources/currency`, update)
      .pipe(
        tap(resources => {
          this.resourcesSubject.next(resources);
        }),
        catchError((error) => this.handleError(error, 'updating currency'))
      );
  }

  /**
   * Convert backend UserResources to WildcardData format for component
   *
   * Note: The 'total' field represents a target or max capacity.
   * In a real implementation, this should come from game rules or user preferences.
   * For now, we'll use a simple calculation based on current values.
   */
  toWildcardData(resources: UserResources): WildcardData {
    // Calculate total as current + some buffer (e.g., showing progress towards a goal)
    // This is a placeholder - adjust based on your business logic
    const calculateTotal = (current: number): number => {
      // Example: show total as current + 20, with minimum of 20
      return Math.max(current + 20, 20);
    };

    return {
      common: {
        current: resources.common_wildcards,
        total: calculateTotal(resources.common_wildcards)
      },
      uncommon: {
        current: resources.uncommon_wildcards,
        total: calculateTotal(resources.uncommon_wildcards)
      },
      rare: {
        current: resources.rare_wildcards,
        total: calculateTotal(resources.rare_wildcards)
      },
      mythic: {
        current: resources.mythic_wildcards,
        total: calculateTotal(resources.mythic_wildcards)
      }
    };
  }

  /**
   * Clear resources cache
   */
  clearResources(): void {
    this.resourcesSubject.next(null);
  }

  /**
   * Private error handler with context
   */
  private handleError(error: HttpErrorResponse, context: string): Observable<never> {
    const sanitizedContext = this.sanitizeContext(context);
    console.error('Error ' + sanitizedContext + ':', error);

    return throwError(() => ({
      ...error,
      context: sanitizedContext,
      timestamp: new Date().toISOString()
    }));
  }

  /**
   * Sanitize context string to prevent format string vulnerabilities
   */
  private sanitizeContext(text: string): string {
    if (!text) {
      return 'unknown operation';
    }

    const str = String(text).trim();
    const maxLength = 150;
    const truncated = str.length > maxLength ? str.substring(0, maxLength) + '...' : str;

    // Remove control characters and other potentially dangerous characters
    const sanitized = truncated.replace(/[^\w\s\-':,./()]/g, '');

    return sanitized || 'unknown operation';
  }
}
