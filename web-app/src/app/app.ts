import { Component, ChangeDetectionStrategy, signal, inject, computed } from '@angular/core';
import { RouterOutlet, RouterLink, Router, NavigationEnd } from '@angular/router';
import { filter, map } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { LoggerService } from './core/logger/logger.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, ToolbarModule, ButtonModule, TooltipModule],
  template: `
    @if (showMenu()) {
      <header class="sticky top-0 z-50 w-full border-b border-surface-200 dark:border-surface-800 bg-surface-0/80 dark:bg-surface-950/80 backdrop-blur-md">
        <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <!-- Logo -->
          <div class="flex items-center gap-2 cursor-pointer group" routerLink="/">
            <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center transition-transform group-hover:scale-110">
              <i class="pi pi-book text-white text-xl"></i>
            </div>
            <span class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-600">
              Foca Notes
            </span>
          </div>

          <!-- Ações -->
          <div class="flex items-center gap-3">
            <p-button 
              label="Nova Anotação" 
              icon="pi pi-plus" 
              severity="primary" 
              [rounded]="true"
              size="small"
              class="hidden sm:block"
            />
            
            <div class="h-6 w-px bg-surface-200 dark:bg-surface-800 mx-1 hidden sm:block"></div>

            <p-button 
              [icon]="isDark() ? 'pi pi-sun' : 'pi pi-moon'" 
              [severity]="isDark() ? 'warn' : 'secondary'" 
              [text]="true" 
              [rounded]="true"
              (onClick)="toggleDarkMode()"
              pTooltip="Alternar Tema"
            />
          </div>
        </div>
      </header>
    }

    <main [class.max-w-6xl]="showMenu()" [class.mx-auto]="showMenu()" [class.px-4]="showMenu()" [class.py-8]="showMenu()">
      <router-outlet />
    </main>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  private logger = inject(LoggerService);
  private router = inject(Router);

  isDark = signal(document.documentElement.classList.contains('p-dark'));

  // Monitora a URL para esconder o menu em rotas específicas
  private currentUrl = toSignal(
    this.router.events.pipe(
      filter((e) => e instanceof NavigationEnd),
      map((e) => (e as NavigationEnd).urlAfterRedirects)
    ),
    { initialValue: this.router.url }
  );

  showMenu = computed(() => {
    const url = this.currentUrl();
    // Esconde se for /auth ou se contiver /create (ajuste conforme suas rotas)
    return !url.includes('/auth') && !url.includes('/create');
  });

  constructor() {
    this.logger.info('Aplicação iniciada');
  }

  toggleDarkMode() {
    const element = document.documentElement;
    if (element.classList.contains('p-dark')) {
      element.classList.remove('p-dark');
      this.isDark.set(false);
      this.logger.info('Tema alterado para: Claro');
    } else {
      element.classList.add('p-dark');
      this.isDark.set(true);
      this.logger.info('Tema alterado para: Escuro');
    }
  }
}
