import {
  ApplicationConfig,
  APP_INITIALIZER,
  inject,
  provideBrowserGlobalErrorListeners,
  ErrorHandler,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';
import { definePreset } from '@primeng/themes';
import { MessageService } from 'primeng/api';
import { catchError, of } from 'rxjs';

import { routes } from './app.routes';
import { apiInterceptor } from './core/http/api.interceptor';
import { AuthService } from './core/auth/auth.service';
import { GlobalErrorHandler } from './core/logger/global-error-handler';

function initAuth() {
  const auth = inject(AuthService);
  return () => auth.loadCurrentUser().pipe(catchError(() => of(null)));
}

// Definindo o preset Violeta baseado no Aura
const VioletPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '{violet.50}',
      100: '{violet.100}',
      200: '{violet.200}',
      300: '{violet.300}',
      400: '{violet.400}',
      500: '{violet.500}',
      600: '{violet.600}',
      700: '{violet.700}',
      800: '{violet.800}',
      900: '{violet.900}',
      950: '{violet.950}',
    },
  },
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([apiInterceptor])),
    provideAnimationsAsync(),
    providePrimeNG({
      theme: {
        preset: VioletPreset,
        options: {
          darkModeSelector: '.p-dark',
        },
      },
    }),
    MessageService,
    { provide: ErrorHandler, useClass: GlobalErrorHandler },
    { provide: APP_INITIALIZER, useFactory: initAuth, multi: true },
  ],
};
