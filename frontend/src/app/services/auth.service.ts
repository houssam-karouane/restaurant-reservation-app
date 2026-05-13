import { Injectable, PLATFORM_ID, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  username: string;
  full_name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
}

const API_URL = 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'auth_token';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly platformId = inject(PLATFORM_ID);
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient) {
    if (this.hasToken()) {
      this.isAuthenticatedSubject.next(true);
      this.getCurrentUser().subscribe({
        next: (user) => {
          this.currentUserSubject.next(user);
        },
        error: () => {
          this.logout();
        },
      });
    }
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${API_URL}/auth/login`, credentials).pipe(
      tap((response) => {
        this.setToken(response.access_token);
        this.currentUserSubject.next(null);
        this.isAuthenticatedSubject.next(true);
      }),
      catchError((error) => {
        console.error('Login failed:', error);
        throw error;
      }),
    );
  }

  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${API_URL}/auth/register`, data).pipe(
      tap((response) => {
        this.setToken(response.access_token);
        this.currentUserSubject.next(null);
        this.isAuthenticatedSubject.next(true);
      }),
      catchError((error) => {
        console.error('Registration failed:', error);
        throw error;
      }),
    );
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${API_URL}/users/me`).pipe(
      tap((user) => {
        this.currentUserSubject.next(user);
      }),
      catchError((error) => {
        console.error('Failed to get current user:', error);
        return of(null as any);
      }),
    );
  }

  logout(): void {
    this.removeToken();
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }

  getToken(): string | null {
    return this.readToken();
  }

  private hasToken(): boolean {
    return !!this.readToken();
  }

  isAuthenticated(): boolean {
    return this.hasToken();
  }

  private readToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    return window.localStorage.getItem(TOKEN_KEY);
  }

  private setToken(token: string): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    window.localStorage.setItem(TOKEN_KEY, token);
  }

  private removeToken(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    window.localStorage.removeItem(TOKEN_KEY);
  }
}
