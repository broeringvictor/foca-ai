import {
  Component,
  ChangeDetectionStrategy,
  inject,
  OnInit,
  signal,
  effect,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { PanelModule } from 'primeng/panel';
import { ProgressBarModule } from 'primeng/progressbar';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

import { StudyService } from '../../services/study.service';
import { StudyAreaProgressDTO, LawArea } from '../../../../core/models/api.models';

@Component({
  selector: 'app-study',
  templateUrl: './study.component.html',
  styleUrls: ['./study.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ButtonModule,
    CardModule,
    PanelModule,
    ProgressBarModule,
    ProgressSpinnerModule,
    TagModule,
    ToastModule,
  ],
  providers: [MessageService],
})
export class StudyComponent implements OnInit {
  private studyService = inject(StudyService);
  private router = inject(Router);
  private messageService = inject(MessageService);

  // State signals
  readonly studyProgress = signal<StudyAreaProgressDTO[]>([]);
  readonly dueAreas = signal<StudyAreaProgressDTO[]>([]);
  readonly progressLoading = signal(false);
  readonly dueLoading = signal(false);
  readonly progressError = signal<Error | null>(null);
  readonly dueError = signal<Error | null>(null);

  // Areas name mapping
  readonly areaNames: Record<LawArea, string> = {
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

  constructor() {
    // Handle progress errors
    effect(() => {
      if (this.progressError()?.message) {
        this.messageService.add({
          severity: 'error',
          summary: 'Erro',
          detail: 'Não foi possível carregar o progresso de estudo',
        });
      }
    });

    // Handle due areas errors
    effect(() => {
      if (this.dueError()?.message) {
        this.messageService.add({
          severity: 'error',
          summary: 'Erro',
          detail: 'Não foi possível carregar as áreas vencidas',
        });
      }
    });
  }

  ngOnInit() {
    this.loadProgressData();
    this.loadDueAreas();
  }

  private loadProgressData() {
    this.progressLoading.set(true);
    this.progressError.set(null);
    this.studyService.getProgress().subscribe({
      next: (data) => {
        this.studyProgress.set(data);
        this.progressLoading.set(false);
      },
      error: (err) => {
        this.progressError.set(err);
        this.progressLoading.set(false);
      },
    });
  }

  private loadDueAreas() {
    this.dueLoading.set(true);
    this.dueError.set(null);
    this.studyService.getDueAreas().subscribe({
      next: (data) => {
        this.dueAreas.set(data);
        this.dueLoading.set(false);
      },
      error: (err) => {
        this.dueError.set(err);
        this.dueLoading.set(false);
      },
    });
  }

  calculateProgress(item: StudyAreaProgressDTO): number {
    const { ease_factor, interval_days } = item.progress;
    const easeProgress = (ease_factor / 5) * 50;
    const intervalProgress = Math.min((interval_days / 100) * 50, 50);
    return Math.round(easeProgress + intervalProgress);
  }

  getStatusSeverityTag(status: number | undefined): 'success' | 'secondary' | 'info' | 'warn' | 'danger' | 'contrast' | null | undefined {
    if (status === undefined) return 'info';
    switch (status) {
      case 0:
        return 'danger';
      case 1:
        return 'warn';
      case 2:
        return 'info';
      case 3:
        return 'success';
      default:
        return 'info';
    }
  }

  getStatusLabel(status: number | undefined): string {
    if (status === undefined) return 'Desconhecido';
    switch (status) {
      case 0:
        return 'Aprendendo';
      case 1:
        return 'Revisão';
      case 2:
        return 'Reaprendendo';
      case 3:
        return 'Dominado';
      default:
        return 'Desconhecido';
    }
  }

  startStudySession() {
    this.router.navigate(['/study-notes/quiz'], {
      queryParams: { session: 'ideal' },
    });
  }

  goToStudyNotes(area: LawArea) {
    this.router.navigate(['/study-notes'], {
      queryParams: { area },
    });
  }

  goToQuiz(area: LawArea) {
    this.router.navigate(['/study-notes/quiz'], {
      queryParams: { area },
    });
  }

  refresh() {
    this.loadProgressData();
    this.loadDueAreas();
  }
}
