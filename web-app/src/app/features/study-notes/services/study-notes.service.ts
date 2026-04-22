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
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar anotacoes';
        return throwError(() => new Error(msg));
      }),
    );
  }

  getById(id: string) {
    // Garante que o ID seja uma string limpa e sem espaços
    const cleanId = String(id).trim();
    return this.http.get<GetStudyNoteResponse>(`/api/v1/study-notes/${cleanId}`).pipe(
      catchError((err) => {
        // Loga o erro completo no console para depuração
        console.error('Erro detalhado do backend:', err.error);
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar anotacao';
        return throwError(() => new Error(msg));
      }),
    );
  }

  getQuestions(id: string) {
    return this.getById(id).pipe(
      switchMap((note) => {
        if (!note.questions || note.questions.length === 0) {
          return of([]);
        }
        const questionRequests = note.questions.map((qId) =>
          this.http.get<Question>(`/api/v1/questions/${qId}`).pipe(
            catchError(() => of(null))
          )
        );
        return forkJoin(questionRequests).pipe(
          map((results) => results.filter((q): q is Question => q !== null))
        );
      }),
      catchError((err) => {
        const msg = err.message ?? 'Erro ao carregar questoes da nota';
        return throwError(() => new Error(msg));
      })
    );
  }
}
