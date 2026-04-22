import { Component, ChangeDetectionStrategy, inject, signal, resource, computed } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Button } from 'primeng/button';
import { Card } from 'primeng/card';
import { Message } from 'primeng/message';
import { Skeleton } from 'primeng/skeleton';
import { Tag } from 'primeng/tag';
import { StudyNotesService } from '../../services/study-notes.service';
import { Question } from '../../../../core/models/api.models';
import { marked } from 'marked';

@Component({
  standalone: true,
  selector: 'app-study-note-detail',
  templateUrl: './study-note-detail.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Button, Card, Message, Skeleton, Tag],
})
export class StudyNoteDetailComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private studyNotesService = inject(StudyNotesService);

  readonly noteId = signal(this.route.snapshot.paramMap.get('id') ?? '');

  readonly noteResource = resource({
    params: this.noteId,
    loader: ({ params: id }) => firstValueFrom(this.studyNotesService.getById(id)),
  });

  readonly questionsResource = resource({
    params: this.noteId,
    loader: ({ params: id }) => firstValueFrom(this.studyNotesService.getQuestions(id)),
  });

  readonly htmlContent = computed(() => {
    const content = this.noteResource.value()?.content;
    return content ? marked.parse(content) : '';
  });

  startQuiz() {
    this.router.navigate(['/study-notes', this.noteId(), 'quiz'], {
      state: { questions: this.questionsResource.value() },
    });
  }

  goBack() {
    this.router.navigate(['/study-notes']);
  }
}
