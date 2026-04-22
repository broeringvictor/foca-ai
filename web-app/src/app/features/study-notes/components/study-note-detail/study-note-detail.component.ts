import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  resource,
  computed,
} from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { firstValueFrom } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { ChipModule } from 'primeng/chip';
import { SkeletonModule } from 'primeng/skeleton';
import { MessageModule } from 'primeng/message';
import { StudyNotesService } from '../../services/study-notes.service';
import { LoggerService } from '../../../../core/logger/logger.service';
import { marked } from 'marked';

@Component({
  standalone: true,
  selector: 'app-study-note-detail',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, ButtonModule, ChipModule, SkeletonModule, MessageModule],
  template: `
    <div class="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      @if (noteResource.isLoading()) {
        <div class="flex flex-col gap-8">
          <p-skeleton width="60%" height="3rem" styleClass="rounded-xl" />
          <div class="space-y-4">
            <p-skeleton width="100%" height="1.25rem" />
            <p-skeleton width="90%" height="1.25rem" />
            <p-skeleton width="95%" height="1.25rem" />
          </div>
        </div>
      } @else if (noteResource.status() === 'error') {
        <div class="flex flex-col items-center justify-center p-20 text-center">
          <i class="pi pi-exclamation-circle text-4xl text-red-500 mb-4"></i>
          <h2 class="text-xl font-bold mb-2">Erro ao carregar nota</h2>
          <p-button label="Voltar para lista" icon="pi pi-arrow-left" (onClick)="goBack()" severity="secondary" [text]="true" />
        </div>
      } @else {
        @let note = noteResource.value();
        <article class="flex flex-col gap-8 animate-in fade-in duration-500">
          <!-- Cabeçalho Principal -->
          <header class="flex flex-col gap-6">
            <div class="flex items-start justify-between gap-4">
              <h1 class="text-4xl font-black tracking-tight text-surface-900 dark:text-surface-0 leading-tight">
                {{ note?.title }}
              </h1>
              <div class="flex items-center gap-2 shrink-0 pt-2">
                <p-button 
                  label="Simulado" 
                  icon="pi pi-bolt" 
                  severity="primary" 
                  [rounded]="true"
                  [loading]="isStartingQuiz()"
                  (onClick)="startQuiz()"
                />
                <p-button 
                  icon="pi pi-arrow-left" 
                  severity="secondary" 
                  [text]="true" 
                  [rounded]="true"
                  (onClick)="goBack()"
                  pTooltip="Voltar"
                />
              </div>
            </div>

            <!-- Tags e Metadados -->
            <div class="flex flex-wrap items-center gap-3">
              @for (tag of note?.tags; track tag) {
                <span class="px-3 py-1 bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-400 text-xs font-bold rounded-full border border-surface-200 dark:border-surface-700">
                  #{{ tag }}
                </span>
              }
              <span class="text-surface-400 text-sm ml-auto hidden sm:block">
                Atualizado em {{ note?.updated_at | date:'dd/MM/yyyy' }}
              </span>
            </div>

            @if (note?.description) {
              <p class="text-xl text-surface-500 dark:text-surface-400 leading-relaxed font-medium italic border-l-4 border-primary/20 pl-6 py-2">
                {{ note?.description }}
              </p>
            }

            <div class="h-px bg-surface-200 dark:bg-surface-800 w-full mt-4"></div>
          </header>

          <!-- Conteúdo Markdown -->
          <section 
            class="markdown-body prose prose-lg dark:prose-invert max-w-none text-surface-800 dark:text-surface-200"
            [innerHTML]="safeHtmlContent()">
          </section>

          <footer class="mt-12 pt-8 border-t border-surface-200 dark:border-surface-800 text-center">
            <p class="text-surface-400 text-sm">Fim da anotação • Bons estudos!</p>
          </footer>
        </article>
      }
    </div>
  `,
  styles: [`
    :host ::ng-deep .markdown-body {
      font-family: 'Inter', -apple-system, sans-serif;
      line-height: 1.8;
      font-size: 1.125rem;
    }
    :host ::ng-deep .markdown-body h1,
    :host ::ng-deep .markdown-body h2,
    :host ::ng-deep .markdown-body h3 {
      color: var(--p-surface-900);
      font-weight: 800;
      letter-spacing: -0.025em;
      margin-top: 2.5rem;
      margin-bottom: 1.25rem;
    }
    .dark :host ::ng-deep .markdown-body h1,
    .dark :host ::ng-deep .markdown-body h2,
    .dark :host ::ng-deep .markdown-body h3 {
      color: var(--p-surface-0);
    }
    :host ::ng-deep .markdown-body h1 { font-size: 2.25rem; border-bottom: 2px solid var(--p-surface-100); padding-bottom: 0.5rem; }
    :host ::ng-deep .markdown-body h2 { font-size: 1.75rem; border-bottom: 1px solid var(--p-surface-100); padding-bottom: 0.25rem; }
    :host ::ng-deep .markdown-body h3 { font-size: 1.35rem; }
    :host ::ng-deep .markdown-body p { margin-bottom: 1.5rem; }
    :host ::ng-deep .markdown-body ul, 
    :host ::ng-deep .markdown-body ol { margin-bottom: 1.5rem; padding-left: 1.5rem; }
    :host ::ng-deep .markdown-body li { margin-bottom: 0.5rem; }
    :host ::ng-deep .markdown-body strong { font-weight: 700; color: var(--p-primary-500); }
    :host ::ng-deep .markdown-body code {
      background: var(--p-surface-100);
      padding: 0.2rem 0.4rem;
      border-radius: 6px;
      font-size: 0.9em;
      font-family: 'Fira Code', monospace;
    }
    .dark :host ::ng-deep .markdown-body code { background: var(--p-surface-800); }
    :host ::ng-deep .markdown-body pre {
      background: var(--p-surface-900);
      color: var(--p-surface-50);
      padding: 1.5rem;
      border-radius: 12px;
      margin: 2rem 0;
      overflow-x: auto;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    :host ::ng-deep .markdown-body blockquote {
      border-left: 4px solid var(--p-primary-500);
      background: var(--p-primary-50);
      padding: 1rem 1.5rem;
      margin: 2rem 0;
      border-radius: 0 12px 12px 0;
      font-style: italic;
    }
    .dark :host ::ng-deep .markdown-body blockquote { background: rgba(var(--p-primary-500-rgb), 0.1); }
  `]
})
export class StudyNoteDetailComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private studyNotesService = inject(StudyNotesService);
  private sanitizer = inject(DomSanitizer);
  private logger = inject(LoggerService);

  readonly noteId = signal(this.route.snapshot.paramMap.get('id') ?? '');
  readonly isStartingQuiz = signal(false);

  readonly noteResource = resource({
    params: this.noteId,
    loader: async ({ params: id }) => {
      this.logger.debug(`Carregando detalhes da nota: ${id}`);
      try {
        const result = await firstValueFrom(this.studyNotesService.getById(id));
        return result;
      } catch (err) {
        this.logger.error(`Erro ao carregar nota ${id}`, err);
        throw err;
      }
    },
  });

  readonly safeHtmlContent = computed<SafeHtml>(() => {
    const content = this.noteResource.value()?.content;
    if (!content) return '';
    const rawHtml = marked.parse(content) as string;
    return this.sanitizer.bypassSecurityTrustHtml(rawHtml);
  });

  async startQuiz() {
    this.logger.info(`Iniciando simulado para a nota: ${this.noteId()}`);
    this.isStartingQuiz.set(true);
    
    try {
      const questions = await firstValueFrom(this.studyNotesService.getQuestions(this.noteId()));
      this.router.navigate(['/study-notes', this.noteId(), 'quiz'], {
        state: { questions },
      });
    } catch (err) {
      this.logger.error('Erro ao buscar questões para o quiz', err);
      this.router.navigate(['/study-notes', this.noteId(), 'quiz']);
    } finally {
      this.isStartingQuiz.set(false);
    }
  }

  goBack() {
    this.router.navigate(['/study-notes']);
  }
}
