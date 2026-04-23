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
import { TooltipModule } from 'primeng/tooltip';
import { StudyNotesService } from '../../services/study-notes.service';
import { LoggerService } from '../../../../core/logger/logger.service';
import { marked } from 'marked';

@Component({
  standalone: true,
  selector: 'app-study-note-detail',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, ButtonModule, ChipModule, SkeletonModule, MessageModule, TooltipModule],
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
              <h1 class="text-4xl font-black tracking-tight text-surface-900 dark:text-surface-950 leading-tight">
                {{ note?.title }}
              </h1>
              <div class="flex items-center gap-2 shrink-0 pt-2">
                @if (note && note.has_embedding !== true && note.embedded !== true) {
                  <p-button 
                    label="Gerar Embeddings" 
                    icon="pi pi-sparkles" 
                    severity="help" 
                    [rounded]="true"
                    [loading]="isGeneratingEmbedding()"
                    (onClick)="onGenerateEmbedding()"
                  />
                }
                
                @if ((note?.has_embedding === true || note?.embedded === true) && (!note?.questions || note?.questions?.length === 0)) {
                  <p-button 
                    label="Buscar Questões" 
                    icon="pi pi-search-plus" 
                    severity="info" 
                    [rounded]="true"
                    [loading]="isSearchingQuestions()"
                    (onClick)="onSearchQuestions()"
                  />
                }
                
                @if ((note?.questions?.length ?? 0) > 0) {
                  <p-button 
                    label="Simulado" 
                    icon="pi pi-bolt" 
                    severity="primary" 
                    [rounded]="true"
                    [loading]="isStartingQuiz()"
                    (onClick)="startQuiz()"
                  />
                }
                
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
                <span class="rounded-full border border-surface-200 bg-surface-100 px-3 py-1 text-xs font-bold text-surface-600 dark:border-surface-700 dark:bg-surface-800 dark:text-surface-300">
                  #{{ tag }}
                </span>
              }
              <span class="ml-auto hidden text-sm text-surface-400 sm:block">
                Atualizado em {{ note?.updated_at | date:'dd/MM/yyyy' }}
              </span>
            </div>

            @if (note?.description) {
              <p class="border-l-4 border-primary/20 py-2 pl-6 text-xl font-medium italic leading-relaxed text-surface-500 dark:text-surface-400">
                {{ note?.description }}
              </p>
            }

            <div class="h-px bg-surface-200 dark:bg-surface-800 w-full mt-4"></div>
          </header>

          <!-- Conteúdo Markdown -->
          <section 
            class="markdown-body prose prose-lg dark:prose-invert max-w-none text-surface-800 dark:text-surface-950"
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
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 1.0625rem;
      line-height: 1.85;
    }

    :host ::ng-deep .markdown-body h1,
    :host ::ng-deep .markdown-body h2,
    :host ::ng-deep .markdown-body h3 {
      color: var(--p-primary-600);
      font-weight: 800;
      letter-spacing: -0.025em;
      margin-bottom: 1rem;
      margin-top: 2.5rem;
    }

    .dark :host ::ng-deep .markdown-body h1,
    .dark :host ::ng-deep .markdown-body h2,
    .dark :host ::ng-deep .markdown-body h3 {
      color: var(--p-primary-400);
    }

    :host ::ng-deep .markdown-body h1 {
      border-bottom: 2px solid var(--p-surface-100);
      font-size: 2.25rem;
      padding-bottom: 0.5rem;
    }

    :host ::ng-deep .markdown-body h2 {
      border-bottom: 1px solid var(--p-surface-100);
      font-size: 1.75rem;
      padding-bottom: 0.25rem;
    }

    :host ::ng-deep .markdown-body h3 {
      font-size: 1.375rem;
    }

    :host ::ng-deep .markdown-body p {
      margin-bottom: 1.25rem;
    }

    :host ::ng-deep .markdown-body ul,
    :host ::ng-deep .markdown-body ol {
      margin-bottom: 1.25rem;
      padding-left: 1.5rem;
    }

    :host ::ng-deep .markdown-body li {
      margin-bottom: 0.5rem;
    }

    :host ::ng-deep .markdown-body strong {
      color: var(--p-primary-500);
      font-weight: 700;
    }

    :host ::ng-deep .markdown-body code {
      background: var(--p-surface-100);
      border-radius: 0.375rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.9em;
      padding: 0.2rem 0.4rem;
    }

    .dark :host ::ng-deep .markdown-body code {
      background: var(--p-surface-200);
      color: var(--p-surface-950);
    }

    :host ::ng-deep .markdown-body pre {
      background: var(--p-surface-900);
      border-radius: 0.875rem;
      color: var(--p-surface-50);
      margin: 2rem 0;
      overflow-x: auto;
      padding: 1.5rem;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.12);
    }

    :host ::ng-deep .markdown-body pre code {
      background: transparent;
      padding: 0;
    }

    :host ::ng-deep .markdown-body blockquote {
      background: var(--p-primary-50);
      border-left: 4px solid var(--p-primary-500);
      border-radius: 0 0.75rem 0.75rem 0;
      font-style: italic;
      margin: 2rem 0;
      padding: 1rem 1.5rem;
    }
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
  readonly isGeneratingEmbedding = signal(false);
  readonly isSearchingQuestions = signal(false);

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

  readonly safeHtmlContent = computed(() => {
    const content = this.noteResource.value()?.content;
    if (!content) return '';
    const rawHtml = marked.parse(content) as string;
    return this.sanitizer.bypassSecurityTrustHtml(rawHtml);
  });

  async onGenerateEmbedding() {
    this.logger.info(`Gerando embeddings para a nota: ${this.noteId()}`);
    this.isGeneratingEmbedding.set(true);
    try {
      await firstValueFrom(this.studyNotesService.generateEmbedding(this.noteId()));
      await this.noteResource.reload();
    } catch (err) {
      this.logger.error('Erro ao gerar embeddings', err);
    } finally {
      this.isGeneratingEmbedding.set(false);
    }
  }

  async onSearchQuestions() {
    this.logger.info(`Buscando questões para a nota: ${this.noteId()}`);
    this.isSearchingQuestions.set(true);
    try {
      await firstValueFrom(this.studyNotesService.searchQuestions(this.noteId()));
      await this.noteResource.reload();
    } catch (err) {
      this.logger.error('Erro ao buscar questões', err);
    } finally {
      this.isSearchingQuestions.set(false);
    }
  }

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
