import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, retry, tap } from 'rxjs/operators';

// Import environment
import { environment } from '../../../environments/environment';

// User interface for authentication
export interface User {
  id: string;
  username: string;
  email: string;
  token?: string;
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

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Base API URL from environment configuration
  private readonly apiUrl = `${environment.apiUrl}/auth`;

  // Current user state
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Load user from local storage on initialization
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      try {
        this.currentUserSubject.next(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('currentUser');
      }
    }
  }

  // Get current user value
  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
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

    return this.http.post<User>(`${this.apiUrl}/login`, credentials)
      .pipe(
        tap(user => {
          // Store user details and token in local storage
          localStorage.setItem('currentUser', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }),
        catchError((error) => this.handleError(error, 'logging in'))
      );
  }

  // Register new user
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

    if (!data.password || data.password.length < 6) {
      return throwError(() => ({
        message: 'Password must be at least 6 characters',
        status: 400,
        timestamp: new Date().toISOString()
      }));
    }

    return this.http.post<User>(`${this.apiUrl}/register`, data)
      .pipe(
        tap(user => {
          // Store user details and token in local storage
          localStorage.setItem('currentUser', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }),
        catchError((error) => this.handleError(error, 'registering user'))
      );
  }

  // Logout user
  logout(): void {
    // Remove user from local storage
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  // Verify token with backend
  verifyToken(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/verify`)
      .pipe(
        retry(1),
        tap(user => {
          localStorage.setItem('currentUser', JSON.stringify(user));
          this.currentUserSubject.next(user);
        }),
        catchError((error) => {
          // If token verification fails, logout user
          this.logout();
          return this.handleError(error, 'verifying token');
        })
      );
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.currentUserValue !== null;
  }

  // Get authentication token
  getToken(): string | null {
    const user = this.currentUserValue;
    return user?.token || null;
  }

  // Private error handler with context
  private handleError(error: HttpErrorResponse, context: string): Observable<never> {
    console.error(`Error ${context}:`, error);

    // Let the interceptor handle the error, but add context
    return throwError(() => ({
      ...error,
      context: context,
      timestamp: new Date().toISOString()
    }));
  }
}
