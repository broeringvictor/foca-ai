import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError, map } from 'rxjs';
import { ListExamsResponse, Exam } from '../../../core/models/api.models';

@Injectable()
export class ExamsService {
  private http = inject(HttpClient);

  list() {
    return this.http.get<ListExamsResponse>('/api/v1/exams/').pipe(
      map((res) => res.exams),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar concursos';
        return throwError(() => new Error(msg));
      }),
    );
  }
}
