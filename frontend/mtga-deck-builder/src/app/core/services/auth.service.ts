import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, retry, tap, switchMap, map } from 'rxjs/operators';

// Import environment
import { environment } from '../../../environments/environment';

// User interface for authentication
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Base API URL from environment configuration
  private readonly apiUrl = `${environment.apiUrl}/auth`;

  // Current auth state
  private authStateSubject = new BehaviorSubject<AuthState>({ user: null, token: null });
  public authState$ = this.authStateSubject.asObservable();
  public currentUser$ = this.authState$.pipe(
    map(state => state.user)
  );

  constructor(private http: HttpClient) {
    // Load auth state from local storage on initialization
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('currentUser');

    if (storedToken && storedUser) {
      try {
        const user = JSON.parse(storedUser);
        this.authStateSubject.next({ user, token: storedToken });
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
        this.clearAuthData();
      }
    }
  }

  // Get current user value
  public get currentUserValue(): User | null {
    return this.authStateSubject.value.user;
  }

  // Get current auth state
  public get authStateValue(): AuthState {
    return this.authStateSubject.value;
  }

  // Login user
  login(credentials: LoginCredentials): Observable<User> {
    if (!credentials || !credentials.username || !credentials.password) {
      return throwError(() => ({
        message: 'Username and password are required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    // Use the JSON login endpoint
    return this.http.post<TokenResponse>(`${this.apiUrl}/login/json`, credentials)
      .pipe(
        // After getting the token, fetch user details
        tap(tokenResponse => {
          // Store token in local storage
          localStorage.setItem('access_token', tokenResponse.access_token);
        }),
        // Switch to fetch user details with the token
        switchMap(tokenResponse => {
          // Temporarily set token so the interceptor can use it
          this.authStateSubject.next({
            user: null,
            token: tokenResponse.access_token
          });
          return this.http.get<User>(`${this.apiUrl}/me`);
        }),
        tap(user => {
          // Store user details in local storage
          localStorage.setItem('currentUser', JSON.stringify(user));
          // Update auth state with both user and token
          const token = localStorage.getItem('access_token')!;
          this.authStateSubject.next({ user, token });
        }),
        catchError((error) => {
          this.clearAuthData();
          return this.handleError(error, 'logging in');
        })
      );
  }

  // Register new user (returns user but doesn't log in automatically)
  register(data: RegisterData): Observable<User> {
    if (!data) {
      return throwError(() => ({
        message: 'Registration data is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!data.username || data.username.trim() === '') {
      return throwError(() => ({
        message: 'Username is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!data.email || data.email.trim() === '') {
      return throwError(() => ({
        message: 'Email is required',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    if (!data.password || data.password.length < 8) {
      return throwError(() => ({
        message: 'Password must be at least 8 characters',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    // Backend registration returns user without token
    // User needs to log in separately after registration
    return this.http.post<User>(`${this.apiUrl}/register`, data)
      .pipe(
        catchError((error) => this.handleError(error, 'registering user'))
      );
  }

  // Logout user
  logout(): void {
    this.clearAuthData();
  }

  // Clear all authentication data
  private clearAuthData(): void {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('access_token');
    this.authStateSubject.next({ user: null, token: null });
  }

  // Verify token with backend
  verifyToken(): Observable<User> {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.clearAuthData();
      return throwError(() => ({
        message: 'No token found',
        status: 401,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.get<User>(`${this.apiUrl}/me`)
      .pipe(
        retry(1),
        tap(user => {
          localStorage.setItem('currentUser', JSON.stringify(user));
          this.authStateSubject.next({ user, token });
        }),
        catchError((error) => {
          // If token verification fails, logout user
          this.clearAuthData();
          return this.handleError(error, 'verifying token');
        })
      );
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.authStateSubject.value.token !== null && this.authStateSubject.value.user !== null;
  }

  // Get authentication token
  getToken(): string | null {
    return this.authStateSubject.value.token;
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
