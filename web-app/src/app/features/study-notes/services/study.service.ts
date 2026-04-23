import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError, map } from 'rxjs';
import {
  ListStudyProgressResponse,
  ListDueAreasResponse,
  SubmitAreaReviewDTO,
  SubmitAreaReviewResponse,
} from '../../../core/models/api.models';

@Injectable()
export class StudyService {
  private http = inject(HttpClient);

  /**
   * Get the next ideal study session (10 questions prioritized by SM-2)
   */
  getStudySession() {
    return this.http.get<ListDueAreasResponse>('/api/v1/study/session').pipe(
      map((res) => res.items),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar sessão de estudo';
        return throwError(() => new Error(msg));
      }),
    );
  }

  /**
   * Get study progress for all areas
   */
  getProgress() {
    return this.http.get<ListStudyProgressResponse>('/api/v1/study/progress').pipe(
      map((res) => res.items),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar progresso de estudo';
        return throwError(() => new Error(msg));
      }),
    );
  }

  /**
   * Get areas due for review with their pre-selected questions (10 per area)
   */
  getDueAreas() {
    return this.http.get<ListDueAreasResponse>('/api/v1/study/due').pipe(
      map((res) => res.items),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar áreas vencidas';
        return throwError(() => new Error(msg));
      }),
    );
  }

  /**
   * Submit a review for a question using SM-2 quality (0 to 5)
   */
  submitReview(review: SubmitAreaReviewDTO) {
    return this.http.post<SubmitAreaReviewResponse>('/api/v1/study/review', review).pipe(
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao submeter revisão';
        return throwError(() => new Error(msg));
      }),
    );
  }
}
