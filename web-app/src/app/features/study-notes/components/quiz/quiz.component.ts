import { Component, ChangeDetectionStrategy, inject, signal, computed, resource } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Button } from 'primeng/button';
import { Card } from 'primeng/card';
import { Message } from 'primeng/message';
import { Tag } from 'primeng/tag';
import { Skeleton } from 'primeng/skeleton';
import { QuestionsService } from '../../services/questions.service';
import { StudyNotesService } from '../../services/study-notes.service';
import { Alternative, CheckAnswerResponse, LawArea, Question } from '../../../../core/models/api.models';

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

@Component({
  standalone: true,
  selector: 'app-quiz',
  templateUrl: './quiz.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Button, Card, Message, Tag, Skeleton],
})
export class QuizComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private questionsService = inject(QuestionsService);
  private studyNotesService = inject(StudyNotesService);

  readonly noteId = signal(this.route.snapshot.paramMap.get('id') ?? '');
  
  readonly questionsResource = resource({
    params: this.noteId,
    loader: ({ params: id }) => {
      const stateQuestions = history.state?.questions as Question[] | undefined;
      if (stateQuestions && stateQuestions.length > 0) {
        return Promise.resolve(stateQuestions);
      }
      return firstValueFrom(this.studyNotesService.getQuestions(id));
    },
  });

  readonly questions = computed(() => this.questionsResource.value() ?? []);
  readonly currentIndex = signal(0);
  readonly currentQuestion = computed(() => this.questions()[this.currentIndex()]);
  readonly selectedAnswer = signal<Alternative | ''>('');
  readonly hasSubmitted = signal(false);
  readonly result = signal<CheckAnswerResponse | null>(null);
  readonly isLoading = signal(false);

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
    if (!this.hasSubmitted()) {
      this.selectedAnswer.set(key);
    }
  }

  async confirmAnswer() {
    const q = this.currentQuestion();
    const answer = this.selectedAnswer();
    if (!q || !answer || this.hasSubmitted()) return;

    this.isLoading.set(true);
    try {
      const result = await firstValueFrom(
        this.questionsService.checkAnswer(q.id, { answer: answer as Alternative }),
      );
      this.result.set(result);
      this.hasSubmitted.set(true);
    } catch {
      // error already handled by service
    } finally {
      this.isLoading.set(false);
    }
  }

  nextQuestion() {
    if (this.currentIndex() < this.questions().length - 1) {
      this.resetState();
      this.currentIndex.update((i) => i + 1);
    }
  }

  prevQuestion() {
    if (this.currentIndex() > 0) {
      this.resetState();
      this.currentIndex.update((i) => i - 1);
    }
  }

  jumpTo(index: number) {
    if (index !== this.currentIndex()) {
      this.resetState();
      this.currentIndex.set(index);
    }
  }

  private resetState() {
    this.selectedAnswer.set('');
    this.hasSubmitted.set(false);
    this.result.set(null);
  }

  goBack() {
    this.router.navigate(['/study-notes', this.noteId()]);
  }
}
