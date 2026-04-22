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
    return this.http.get<GetStudyNoteResponse>(`/api/v1/study-notes/${id}`).pipe(
      catchError((err) => {
        const msg = err.error?.detail?.[0]?.message ?? 'Erro ao carregar anotacao';
        return throwError(() => new Error(msg));
      }),
    );
  }

  /**
   * Como não existe um endpoint direto para listar detalhes das questões de uma nota,
   * primeiro buscamos a nota (que contém os IDs das questões) e depois buscamos cada questão.
   */
  getQuestions(id: string) {
    return this.getById(id).pipe(
      switchMap((note) => {
        if (!note.questions || note.questions.length === 0) {
          return of([]);
        }
        // Busca os detalhes de cada questão pelo ID
        const questionRequests = note.questions.map((qId) =>
          this.http.get<Question>(`/api/v1/questions/${qId}`).pipe(
            catchError(() => of(null)) // Ignora questões individuais que falharem
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
