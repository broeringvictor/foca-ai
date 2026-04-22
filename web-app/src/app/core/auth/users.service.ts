import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { RegisterDTO } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class UsersService {
  private http = inject(HttpClient);

  register(dto: RegisterDTO) {
    return this.http.post('/api/v1/users/', dto).pipe(
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao cadastrar';
        return throwError(() => new Error(msg));
      }),
    );
  }
}
