import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';

export const apiInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  const url = req.url.startsWith('/api')
    ? `${environment.apiUrl}${req.url}`
    : req.url;

  const cloned = req.clone({ url, withCredentials: true });

  return next(cloned).pipe(
    catchError((err) => {
      if (err.status === 401) {
        router.navigate(['/auth']);
      }
      return throwError(() => err);
    }),
  );
};
