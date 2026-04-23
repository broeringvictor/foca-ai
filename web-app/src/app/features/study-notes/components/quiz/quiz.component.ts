import { Component, ChangeDetectionStrategy, inject, signal, computed, resource } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { firstValueFrom } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { TagModule } from 'primeng/tag';
import { SkeletonModule } from 'primeng/skeleton';
import { TooltipModule } from 'primeng/tooltip';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { QuestionsService } from '../../services/questions.service';
import { StudyNotesService } from '../../services/study-notes.service';
import { StudyService } from '../../services/study.service';
import { 
  Alternative, 
  CheckAnswerResponse, 
  LawArea, 
  Question, 
  SubmitAreaReviewResponse,
  Sm2Progress
} from '../../../../core/models/api.models';
import { LoggerService } from '../../../../core/logger/logger.service';

const LAW_AREA_LABELS: Record<LawArea, string> = {
  direito_constitucional: 'Direito Constitucional',
  direitos_humanos: 'Direitos Humanos',
  etica_profissional: 'Ética Profissional',
  filosofia_do_direito: 'Filosofia do Direito',
  direito_internacional: 'Direito Internacional',
  direito_tributario: 'Direito Tributário',
  direito_administrativo: 'Direito Administrativo',
  direito_ambiental: 'Direito Ambiental',
  direito_civil: 'Direito Civil',
  direito_do_consumidor: 'Direito do Consumidor',
  eca: 'ECA',
  direito_empresarial: 'Direito Empresarial',
  direito_penal: 'Direito Penal',
  direito_processual_civil: 'Direito Processual Civil',
  direito_processual_penal: 'Direito Processual Penal',
  direito_do_trabalho: 'Direito do Trabalho',
  direito_processual_do_trabalho: 'Direito Processual do Trabalho',
  direito_previdenciario: 'Direito Previdenciário',
  direito_financeiro: 'Direito Financeiro',
};

interface QuestionState {
  selectedAnswer: Alternative | '';
  hasSubmitted: boolean;
  result: CheckAnswerResponse | SubmitAreaReviewResponse | null;
  error?: string;
  selectedQuality?: number;
}

@Component({
  standalone: true,
  selector: 'app-quiz',
  templateUrl: './quiz.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule, 
    ButtonModule, 
    CardModule, 
    MessageModule, 
    TagModule, 
    SkeletonModule, 
    TooltipModule,
    ProgressSpinnerModule
  ],
})
export class QuizComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private questionsService = inject(QuestionsService);
  private studyNotesService = inject(StudyNotesService);
  private studyService = inject(StudyService);
  private logger = inject(LoggerService);

  readonly noteId = signal(this.route.snapshot.paramMap.get('id') ?? '');
  readonly areaQuery = signal<LawArea | null>(this.route.snapshot.queryParamMap.get('area') as LawArea);
  readonly sessionQuery = signal<string | null>(this.route.snapshot.queryParamMap.get('session'));
  
  // Local state for study mode questions
  private studyQuestions = signal<Question[]>([]);
  readonly isStudyMode = computed(() => !!this.areaQuery() || !!this.sessionQuery());

  readonly questionsResource = resource({
    params: () => ({ noteId: this.noteId(), area: this.areaQuery(), session: this.sessionQuery() }),
    loader: async ({ params }) => {
      // General Study Session (Ideal questions)
      if (params.session === 'ideal') {
        this.logger.debug('Carregando sessão de estudo ideal');
        try {
          const areas = await firstValueFrom(this.studyService.getStudySession());
          // Flatten all questions from all areas returned in the session
          const allQuestions = areas.flatMap(a => a.questions);
          this.studyQuestions.set(allQuestions);
          return allQuestions;
        } catch (err: any) {
          this.logger.error('Erro ao carregar sessão de estudo ideal', err);
          throw err;
        }
      }

      // Specific Area Study
      if (params.area) {
        this.logger.debug(`Carregando questões vencidas para a área ${params.area}`);
        try {
          const areas = await firstValueFrom(this.studyService.getDueAreas());
          const areaData = areas.find(a => a.area === params.area);
          if (areaData) {
            this.studyQuestions.set(areaData.questions);
            return areaData.questions;
          }
          return [] as Question[];
        } catch (err: any) {
          this.logger.error(`Erro ao carregar questões vencidas para ${params.area}`, err);
          throw err;
        }
      }

      this.logger.debug(`Carregando questões para o quiz da nota ${params.noteId}`);
      const stateQuestions = history.state?.questions as Question[] | undefined;
      if (stateQuestions && stateQuestions.length > 0) {
        return Promise.resolve(stateQuestions);
      }
      try {
        return await firstValueFrom(this.studyNotesService.getQuestions(params.noteId));
      } catch (err: any) {
        this.logger.error(`Erro ao carregar questões para a nota ${params.noteId}`, err);
        throw err;
      }
    },
  });

  readonly questions = computed<Question[]>(() => {
    if (this.isStudyMode()) return this.studyQuestions();
    return (this.questionsResource.value() as Question[]) ?? [];
  });

  readonly currentIndex = signal(0);
  readonly currentQuestion = computed<Question | undefined>(() => this.questions()[this.currentIndex()]);
  
  protected states = signal<Map<string, QuestionState>>(new Map());

  readonly currentState = computed(() => {
    const q = this.currentQuestion();
    if (!q) return { selectedAnswer: '', hasSubmitted: false, result: null } as QuestionState;
    return this.states().get(q.id) || { selectedAnswer: '', hasSubmitted: false, result: null } as QuestionState;
  });

  readonly isLoading = signal(false);
  readonly globalError = signal<string | null>(null);
  readonly areaLabels = LAW_AREA_LABELS;

  // Track new progress from SM-2
  readonly sm2Progress = signal<Sm2Progress | null>(null);

  getAlternatives(q: Question) {
    return [
      { key: 'A' as Alternative, text: q.alternative_a },
      { key: 'B' as Alternative, text: q.alternative_b },
      { key: 'C' as Alternative, text: q.alternative_c },
      { key: 'D' as Alternative, text: q.alternative_d },
    ];
  }

  getCorrectAnswer(result: CheckAnswerResponse | SubmitAreaReviewResponse | null): string {
    if (!result) return '';
    if ('correct_alternative' in result) return result.correct_alternative;
    if ('correct_answer' in result) return result.correct_answer || '';
    return '';
  }

  selectAnswer(key: Alternative) {
    const q = this.currentQuestion();
    if (!q || this.currentState().hasSubmitted) return;
    
    // In study mode, initialize with default quality 4 (GOOD)
    const partialState: Partial<QuestionState> = { selectedAnswer: key, error: undefined };
    if (this.isStudyMode()) {
      partialState.selectedQuality = 4;
    }
    
    this.updateState(q.id, partialState);
  }

  async confirmAnswer() {
    const q = this.currentQuestion();
    const state = this.currentState();
    
    if (!q || !state.selectedAnswer || state.hasSubmitted || this.isLoading()) return;

    this.logger.info(`Submetendo revisão da questão ${q.id}...`);
    this.isLoading.set(true);
    this.globalError.set(null);

    try {
      if (this.isStudyMode()) {
        // Send selected answer and quality in one go
        const result = await firstValueFrom(
          this.studyService.submitReview({
            question_id: q.id,
            response: state.selectedAnswer as Alternative,
            quality: state.selectedQuality ?? 4
          })
        );
        
        this.updateState(q.id, { 
          hasSubmitted: true, 
          result, 
          error: undefined 
        });
        
        this.sm2Progress.set(result.new_progress);
      } else {
        // Standard quiz mode (from a note)
        const result = await firstValueFrom(
          this.questionsService.checkAnswer(q.id, { answer: state.selectedAnswer as Alternative })
        );
        this.updateState(q.id, { hasSubmitted: true, result, error: undefined });
      }
    } catch (err: any) {
      let errorMsg = 'Erro de conexão. Verifique sua internet.';
      if (err.status === 404) errorMsg = 'Questão não encontrada.';
      if (err.status >= 500) errorMsg = 'Erro no servidor.';
      
      this.updateState(q.id, { error: errorMsg });
      this.logger.error(`Erro ao validar questão ${q.id}`, err);
    } finally {
      this.isLoading.set(false);
    }
  }

  async selectQuality(quality: number) {
    const q = this.currentQuestion();
    const state = this.currentState();
    if (!q || !this.isStudyMode()) return;

    // Update local state before submission
    this.updateState(q.id, { selectedQuality: quality });

    // If already submitted, we could optionally allow re-submitting to update quality,
    // but typically SM-2 is one-shot per review session.
    if (state.hasSubmitted) {
      this.isLoading.set(true);
      try {
        const result = await firstValueFrom(
          this.studyService.submitReview({
            question_id: q.id,
            response: state.selectedAnswer as Alternative,
            quality
          })
        );
        this.sm2Progress.set(result.new_progress);
      } catch (err) {
        this.logger.error('Erro ao atualizar qualidade pós-envio', err);
      } finally {
        this.isLoading.set(false);
      }
    }
  }

  async nextQuestion() {
    if (this.currentIndex() < this.questions().length - 1) {
      this.currentIndex.update((i) => i + 1);
      // Reset sm2Progress for the new question view in study mode
      if (this.isStudyMode()) {
        this.sm2Progress.set(null);
      }
    } else if (this.isStudyMode()) {
      // Load more questions if we finished the 10-batch and we are in study mode
      await this.loadMoreStudyQuestions();
    }
  }

  private async loadMoreStudyQuestions() {
    this.isLoading.set(true);
    try {
      let questions: Question[] = [];
      
      if (this.sessionQuery() === 'ideal') {
        const areas = await firstValueFrom(this.studyService.getStudySession());
        questions = areas.flatMap(a => a.questions);
      } else if (this.areaQuery()) {
        const areas = await firstValueFrom(this.studyService.getDueAreas());
        const areaData = areas.find(a => a.area === this.areaQuery());
        questions = areaData?.questions || [];
      }

      if (questions.length > 0) {
        this.studyQuestions.set(questions);
        this.currentIndex.set(0);
        // Reset states for the new questions
        this.states.set(new Map());
      } else {
        // No more questions
        this.goBack();
      }
    } catch (err) {
      this.logger.error('Erro ao carregar mais questões', err);
    } finally {
      this.isLoading.set(false);
    }
  }

  prevQuestion() {
    if (this.currentIndex() > 0) {
      this.currentIndex.update((i) => i - 1);
    }
  }

  jumpTo(index: number) {
    if (index >= 0 && index < this.questions().length) {
      this.currentIndex.set(index);
    }
  }

  private updateState(questionId: string, partial: Partial<QuestionState>) {
    this.states.update(map => {
      const current = map.get(questionId) || { selectedAnswer: '', hasSubmitted: false, result: null };
      map.set(questionId, { ...current, ...partial });
      return new Map(map);
    });
  }

  goBack() {
    if (this.isStudyMode()) {
      this.router.navigate(['/study-notes/study']);
    } else {
      this.router.navigate(['/study-notes', this.noteId()]);
    }
  }
}
