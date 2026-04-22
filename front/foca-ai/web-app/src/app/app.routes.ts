import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'study-notes', pathMatch: 'full' },
  {
    path: 'auth',
    loadComponent: () => import('./features/auth/auth.component').then((m) => m.AuthComponent),
  },
  {
    path: 'study-notes',
    canMatch: [authGuard],
    loadChildren: () => import('./features/study-notes/study-notes.routes'),
  },
  { path: '**', redirectTo: 'study-notes' },
];
