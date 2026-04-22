import { Component, ChangeDetectionStrategy, inject, resource } from '@angular/core';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Card } from 'primeng/card';
import { Skeleton } from 'primeng/skeleton';
import { Message } from 'primeng/message';
import { Button } from 'primeng/button';
import { Tag } from 'primeng/tag';
import { Tooltip } from 'primeng/tooltip';
import { StudyNotesService } from '../../services/study-notes.service';

@Component({
  standalone: true,
  selector: 'app-study-notes-list',
  templateUrl: './study-notes-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Card, Skeleton, Message, Button, Tag, Tooltip],
})
export class StudyNotesListComponent {
  private router = inject(Router);
  private studyNotesService = inject(StudyNotesService);

  readonly notes = resource({
    loader: () => firstValueFrom(this.studyNotesService.list()),
  });

  readonly skeletons = Array(6).fill(null);

  navigateTo(id: string) {
    this.router.navigate(['/study-notes', id]);
  }
}
