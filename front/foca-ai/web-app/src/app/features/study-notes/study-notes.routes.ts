import { Routes } from '@angular/router';
import { StudyNotesService } from './services/study-notes.service';
import { ExamsService } from './services/exams.service';
import { QuestionsService } from './services/questions.service';

export default [
  {
    path: '',
    providers: [StudyNotesService, ExamsService, QuestionsService],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./components/study-notes-list/study-notes-list.component').then(
            (m) => m.StudyNotesListComponent,
          ),
      },
      {
        path: ':id',
        loadComponent: () =>
          import('./components/study-note-detail/study-note-detail.component').then(
            (m) => m.StudyNoteDetailComponent,
          ),
      },
      {
        path: ':id/quiz',
        loadComponent: () =>
          import('./components/quiz/quiz.component').then((m) => m.QuizComponent),
      },
    ],
  },
] satisfies Routes;
