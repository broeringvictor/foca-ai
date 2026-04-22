import { Component, ChangeDetectionStrategy, signal, inject } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';
import { LoggerService } from './core/logger/logger.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, ToolbarModule, ButtonModule],
  template: `
    <header class="sticky top-0 z-50 w-full border-b border-surface-200 dark:border-surface-800 bg-surface-0/80 dark:bg-surface-950/80 backdrop-blur-md">
      <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <!-- Logo Centralizada no Mobile / Esquerda no Desktop -->
        <div class="flex items-center gap-2 cursor-pointer group" routerLink="/">
          <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center transition-transform group-hover:scale-110">
            <i class="pi pi-book text-white text-xl"></i>
          </div>
          <span class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-600">
            Foca Notes
          </span>
        </div>

        <!-- Ações Direita -->
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

    <main class="max-w-6xl mx-auto px-4 py-8">
      <router-outlet />
    </main>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  private logger = inject(LoggerService);
  isDark = signal(document.documentElement.classList.contains('p-dark'));

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
