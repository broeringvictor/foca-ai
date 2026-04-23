import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: 'auth',
    loadComponent: () => import('./features/auth/auth.component').then((m) => m.AuthComponent),
  },
  {
    path: '',
    loadComponent: () =>
      import('./core/layout/shell/shell.component').then((m) => m.ShellComponent),
    canMatch: [authGuard],
    children: [
      { path: '', redirectTo: 'study-notes/study', pathMatch: 'full' },
      {
        path: 'study-notes',
        loadChildren: () => import('./features/study-notes/study-notes.routes'),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
