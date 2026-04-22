import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, switchMap, tap } from 'rxjs';
import { AuthenticateDTO, AuthenticateResponse, GetMeResponse } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _currentUser = signal<GetMeResponse | null>(null);
  readonly currentUser = this._currentUser.asReadonly();
  readonly isAuthenticated = computed(() => this._currentUser() !== null);

  login(dto: AuthenticateDTO): Observable<GetMeResponse> {
    return this.http.post<AuthenticateResponse>('/api/v1/auth/authenticate', dto).pipe(
      switchMap(() => this.loadCurrentUser()),
    );
  }

  loadCurrentUser(): Observable<GetMeResponse> {
    return this.http.get<GetMeResponse>('/api/v1/users/me').pipe(
      tap((user: GetMeResponse) => this._currentUser.set(user)),
    );
  }

  logout(): void {
    this._currentUser.set(null);
    this.router.navigate(['/auth']);
  }
}
