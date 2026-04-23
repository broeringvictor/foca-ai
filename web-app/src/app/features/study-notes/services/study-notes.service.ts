import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError, map, switchMap, forkJoin, of } from 'rxjs';
import { 
  ListStudyNotesResponse, 
  StudyNoteListItem, 
  GetStudyNoteResponse, 
  Question 
} from '../../../core/models/api.models';

@Injectable()
export class StudyNotesService {
  private http = inject(HttpClient);

  list() {
    return this.http.get<ListStudyNotesResponse>('/api/v1/study-notes/').pipe(
      map((res) => res.items),
      catchError((err) => {
        const msg = this.extractErrorMessage(err);
        return throwError(() => new Error(msg));
      }),
    );
  }

  getById(id: string) {
    // URL limpa conforme documentação
    const url = `/api/v1/study-notes/${id.trim()}`;
    return this.http.get<GetStudyNoteResponse>(url).pipe(
      catchError((err) => {
        // Se o erro for 422 no 'questions → 0', o problema é no dado retornado pelo servidor
        console.error('Erro de validacao no backend (Response Validation Failure):', err.error);
        const msg = this.extractErrorMessage(err);
        return throwError(() => new Error(msg));
      }),
    );
  }

  getQuestions(id: string) {
    return this.getById(id).pipe(
      switchMap((note) => {
        // Se a nota vier, mas questions for nulo ou vazio
        if (!note || !note.questions || note.questions.length === 0) {
          return of([]);
        }
        
        const questionRequests = note.questions.map((qId) => {
          // Garante que qId seja string antes de concatenar
          const cleanQId = typeof qId === 'string' ? qId : (qId as any).id || String(qId);
          return this.http.get<Question>(`/api/v1/questions/${cleanQId}`).pipe(
            catchError((err) => {
              console.error(`Erro ao carregar questao ${cleanQId}:`, err);
              return of(null);
            })
          );
        });

        return forkJoin(questionRequests).pipe(
          map((results) => results.filter((q): q is Question => q !== null))
        );
      }),
      catchError((err) => {
        const msg = err.message || 'Erro ao processar questoes';
        return throwError(() => new Error(msg));
      })
    );
  }

  generateEmbedding(id: string) {
    return this.http.post<any>(`/api/v1/study-notes/${id}/embeddings`, {}).pipe(
      catchError((err) => {
        const msg = this.extractErrorMessage(err);
        return throwError(() => new Error(msg));
      })
    );
  }

  searchQuestions(id: string) {
    return this.http.post<any>(`/api/v1/study-notes/${id}/questions`, {}).pipe(
      catchError((err) => {
        const msg = this.extractErrorMessage(err);
        return throwError(() => new Error(msg));
      })
    );
  }

  private extractErrorMessage(err: any): string {
    const detail = err.error?.detail;
    if (Array.isArray(detail) && detail.length > 0) {
      // Formata o erro de campo para algo legível
      const d = detail[0];
      if (d.field && d.message) return `${d.field}: ${d.message}`;
      return d.msg || d.message || 'Erro de validacao';
    }
    return err.error?.message || err.message || 'Erro no servidor';
  }
}
