import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError, map } from 'rxjs';
import {
  ListQuestionsResponse,
  CheckAnswerDTO,
  CheckAnswerResponse,
} from '../../../core/models/api.models';

@Injectable()
export class QuestionsService {
  private http = inject(HttpClient);

  listByExam(examId: string) {
    return this.http.get<ListQuestionsResponse>(`/api/v1/questions/exam/${examId}`).pipe(
      map((res) => res.questions),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar questões';
        return throwError(() => new Error(msg));
      }),
    );
  }

  checkAnswer(questionId: string, dto: CheckAnswerDTO) {
    return this.http
      .post<CheckAnswerResponse>(`/api/v1/questions/${questionId}/check`, dto)
      .pipe(
        catchError((err) => {
          const msg = err.error?.detail?.[0]?.message ?? 'Erro ao verificar resposta';
          return throwError(() => new Error(msg));
        }),
      );
  }
}
