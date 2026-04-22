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
import { Alternative, CheckAnswerResponse, LawArea, Question } from '../../../../core/models/api.models';
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
  result: CheckAnswerResponse | null;
  error?: string;
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
  private logger = inject(LoggerService);

  readonly noteId = signal(this.route.snapshot.paramMap.get('id') ?? '');
  
  readonly questionsResource = resource({
    params: this.noteId,
    loader: async ({ params: id }) => {
      this.logger.debug(`Carregando questões para o quiz da nota ${id}`);
      const stateQuestions = history.state?.questions as Question[] | undefined;
      if (stateQuestions && stateQuestions.length > 0) {
        return Promise.resolve(stateQuestions);
      }
      try {
        return await firstValueFrom(this.studyNotesService.getQuestions(id));
      } catch (err: any) {
        this.logger.error(`Erro ao carregar questões para a nota ${id}`, err);
        throw err;
      }
    },
  });

  readonly questions = computed(() => this.questionsResource.value() ?? []);
  readonly currentIndex = signal(0);
  readonly currentQuestion = computed(() => this.questions()[this.currentIndex()]);
  
  protected states = signal<Map<string, QuestionState>>(new Map());

  readonly currentState = computed(() => {
    const q = this.currentQuestion();
    if (!q) return { selectedAnswer: '', hasSubmitted: false, result: null } as QuestionState;
    return this.states().get(q.id) || { selectedAnswer: '', hasSubmitted: false, result: null } as QuestionState;
  });

  readonly isLoading = signal(false);
  readonly globalError = signal<string | null>(null);
  readonly areaLabels = LAW_AREA_LABELS;

  getAlternatives(q: Question) {
    return [
      { key: 'A' as Alternative, text: q.alternative_a },
      { key: 'B' as Alternative, text: q.alternative_b },
      { key: 'C' as Alternative, text: q.alternative_c },
      { key: 'D' as Alternative, text: q.alternative_d },
    ];
  }

  selectAnswer(key: Alternative) {
    const q = this.currentQuestion();
    if (!q || this.currentState().hasSubmitted) return;
    this.updateState(q.id, { selectedAnswer: key, error: undefined });
  }

  async confirmAnswer() {
    const q = this.currentQuestion();
    const state = this.currentState();
    
    if (!q || !state.selectedAnswer || state.hasSubmitted || this.isLoading()) return;

    this.logger.info(`Validando resposta da questão ${q.id}...`);
    this.isLoading.set(true);
    this.globalError.set(null);

    try {
      // Simula um delay pequeno para o usuário sentir que está "enviando"
      const result = await firstValueFrom(
        this.questionsService.checkAnswer(q.id, { answer: state.selectedAnswer as Alternative })
      );
      
      this.updateState(q.id, { hasSubmitted: true, result, error: undefined });
      this.logger.info(`Questão ${q.id} validada com sucesso.`);
    } catch (err: any) {
      let errorMsg = 'Erro de conexão. Verifique sua internet.';
      if (err.status === 404) errorMsg = 'Questão não encontrada no servidor.';
      if (err.status >= 500) errorMsg = 'Erro interno do servidor. Tente mais tarde.';
      
      this.updateState(q.id, { error: errorMsg });
      this.logger.error(`Erro ao validar questão ${q.id}`, err);
    } finally {
      this.isLoading.set(false);
    }
  }

  nextQuestion() {
    if (this.currentIndex() < this.questions().length - 1) {
      this.currentIndex.update((i) => i + 1);
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
    this.router.navigate(['/study-notes', this.noteId()]);
  }
}
