import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface User {
  id: string;
  email: string;
  name: string;
}

const API_URL = 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'auth_token';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(this.getUserFromStorage());
  public currentUser$ = this.currentUserSubject.asObservable();

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient) {
    // Try to validate token on service initialization
    if (this.hasToken()) {
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
        localStorage.setItem(TOKEN_KEY, response.access_token);
        this.isAuthenticatedSubject.next(true);
      }),
      catchError((error) => {
        console.error('Login failed:', error);
        throw error;
      })
    );
  }

  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${API_URL}/auth/register`, data).pipe(
      tap((response) => {
        localStorage.setItem(TOKEN_KEY, response.access_token);
        this.isAuthenticatedSubject.next(true);
      }),
      catchError((error) => {
        console.error('Registration failed:', error);
        throw error;
      })
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
      })
    );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return this.hasToken();
  }
}
