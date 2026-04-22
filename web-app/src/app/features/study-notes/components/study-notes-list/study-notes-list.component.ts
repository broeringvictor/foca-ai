import { Component, ChangeDetectionStrategy, inject, resource } from '@angular/core';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { SkeletonModule } from 'primeng/skeleton';
import { TagModule } from 'primeng/tag';
import { InputTextModule } from 'primeng/inputtext';
import { StudyNotesService } from '../../services/study-notes.service';
import { LoggerService } from '../../../../core/logger/logger.service';

@Component({
  standalone: true,
  selector: 'app-study-notes-list',
  templateUrl: './study-notes-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ButtonModule, SkeletonModule, TagModule, InputTextModule],
})
export class StudyNotesListComponent {
  private router = inject(Router);
  private studyNotesService = inject(StudyNotesService);
  private logger = inject(LoggerService);

  readonly notes = resource({
    loader: async () => {
      this.logger.debug('Carregando lista de anotações...');
      try {
        const result = await firstValueFrom(this.studyNotesService.list());
        this.logger.info(`Lista de anotações carregada com ${result.length} itens`);
        return result;
      } catch (err) {
        this.logger.error('Erro ao carregar lista de anotações', err);
        throw err;
      }
    },
  });

  readonly skeletons = Array(6).fill(null);

  navigateTo(id: string) {
    this.logger.info(`Navegando para detalhes da nota: ${id}`);
    this.router.navigate(['/study-notes', id]);
  }
}
