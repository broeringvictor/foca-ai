import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError, map } from 'rxjs';
import { ListStudyNotesResponse, StudyNoteListItem, GetStudyNoteResponse, ListQuestionsResponse } from '../../../core/models/api.models';

@Injectable()
export class StudyNotesService {
  private http = inject(HttpClient);

  list() {
    return this.http.get<ListStudyNotesResponse>('/api/v1/study-notes/').pipe(
      map((res) => res.items),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar anotações';
        return throwError(() => new Error(msg));
      }),
    );
  }

  getById(id: string) {
    return this.http.get<GetStudyNoteResponse>(`/api/v1/study-notes/${id}`).pipe(
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar anotação';
        return throwError(() => new Error(msg));
      }),
    );
  }

  getQuestions(id: string) {
    return this.http.get<ListQuestionsResponse>(`/api/v1/study-notes/${id}/questions`).pipe(
      map((res) => res.questions),
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar questões';
        return throwError(() => new Error(msg));
      }),
    );
  }
}
