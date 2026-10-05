import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, LoginResponse, RegisterRequest, RegisterResponse, UserRole } from '../../shared/models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;

  // Reactive state management using Angular signals
  private _currentUser = signal<User | null>(null);
  readonly currentUser = this._currentUser.asReadonly();

  readonly isAuthenticated = computed(() => !!this._currentUser());
  readonly userRole = computed<UserRole | null>(() => this._currentUser()?.role || null);
  readonly isAdmin = computed(() => this._currentUser()?.role === 'ADMIN' || this._currentUser()?.is_staff === true);
  readonly isSupportStaff = computed(() => {
    const role = this._currentUser()?.role;
    return role === 'AGENT' || role === 'ADMIN' || this._currentUser()?.is_staff === true;
  });

  constructor(private http: HttpClient, private router: Router) {
    this.initAuthFromStorage();
  }

  private initAuthFromStorage(): void {
    try {
      const storedUser = localStorage.getItem('tp_user');
      const token = localStorage.getItem('tp_access_token');
      if (storedUser && token) {
        this._currentUser.set(JSON.parse(storedUser));
      }
    } catch (e) {
      console.error('Error loading stored session:', e);
      this.clearSession();
    }
  }

  login(credentials: { email: string; password: string }): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, credentials).pipe(
      tap((res) => {
        this.saveSession(res.access, res.refresh, res.user);
      })
    );
  }

  register(data: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.apiUrl}/register/`, data).pipe(
      tap((res) => {
        this.saveSession(res.tokens.access, res.tokens.refresh, res.user);
      })
    );
  }

  logout(): void {
    this.clearSession();
    this.router.navigate(['/auth/login']);
  }

  getAccessToken(): string | null {
    return localStorage.getItem('tp_access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('tp_refresh_token');
  }

  refreshAccessToken(): Observable<{ access: string }> {
    const refresh = this.getRefreshToken();
    return this.http.post<{ access: string }>(`${this.apiUrl}/refresh/`, { refresh }).pipe(
      tap((res) => {
        localStorage.setItem('tp_access_token', res.access);
      })
    );
  }

  private saveSession(access: string, refresh: string, user: User): void {
    localStorage.setItem('tp_access_token', access);
    localStorage.setItem('tp_refresh_token', refresh);
    localStorage.setItem('tp_user', JSON.stringify(user));
    this._currentUser.set(user);
  }

  private clearSession(): void {
    localStorage.removeItem('tp_access_token');
    localStorage.removeItem('tp_refresh_token');
    localStorage.removeItem('tp_user');
    this._currentUser.set(null);
  }
}
