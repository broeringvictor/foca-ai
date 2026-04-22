import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/app_exception.dart';
import '../../../core/ui/error_display.dart';
import '../../auth/presentation/auth_state_notifier.dart';
import 'study_note_detail_notifier.dart';
import 'widgets/knn_search_sheet.dart';
import 'widgets/question_list_tile.dart';
import 'widgets/related_question_card.dart';

class StudyNoteDetailScreen extends ConsumerWidget {
  final String noteId;

  const StudyNoteDetailScreen({super.key, required this.noteId});

  void _showKnnSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => KnnSearchSheet(noteId: noteId),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stateAsync = ref.watch(studyNoteDetailProvider(noteId));

    ref.listen(studyNoteDetailProvider(noteId), (_, next) {
      if (next.hasError) {
        final err = next.error;
        final message = err is ApiException ? err.firstMessage : 'Erro ao carregar nota';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    });

    return stateAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(),
        body: ErrorDisplay(
          exception: err is AppException ? err : UnknownException(err),
          onRetry: () => ref.invalidate(studyNoteDetailProvider(noteId)),
        ),
      ),
      data: (state) => _DetailContent(
        noteId: noteId,
        state: state,
        onShowKnnSheet: () => _showKnnSheet(context),
      ),
    );
  }
}

class _DetailContent extends ConsumerWidget {
  final String noteId;
  final StudyNoteDetailState state;
  final VoidCallback onShowKnnSheet;

  const _DetailContent({
    required this.noteId,
    required this.state,
    required this.onShowKnnSheet,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final hasQuestions = state.questionList.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          state.note.title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            tooltip: 'Sair',
            onPressed: () => ref.read(authStateProvider.notifier).logout(),
          ),
        ],
      ),
      body: CustomScrollView(
        slivers: [
          // Conteúdo Markdown da nota
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
              child: _NoteContent(note: state.note),
            ),
          ),

          // Tags
          if (state.note.tags.isNotEmpty)
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: Wrap(
                  spacing: 8,
                  children: state.note.tags
                      .map(
                        (tag) => Chip(
                          label: Text(tag),
                          visualDensity: VisualDensity.compact,
                          backgroundColor: theme.colorScheme.secondaryContainer,
                          labelStyle: TextStyle(
                            color: theme.colorScheme.onSecondaryContainer,
                            fontSize: 12,
                          ),
                        ),
                      )
                      .toList(),
                ),
              ),
            ),

          // Divisor
          const SliverToBoxAdapter(child: SizedBox(height: 24)),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Text(
                    'Questões da nota',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const Spacer(),
                  FilledButton.tonalIcon(
                    onPressed: onShowKnnSheet,
                    icon: const Icon(Icons.search_rounded, size: 18),
                    label: const Text('Buscar'),
                  ),
                ],
              ),
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 12)),

          // Lista de questões salvas
          if (!hasQuestions)
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(
                      Icons.quiz_outlined,
                      size: 48,
                      color: theme.colorScheme.outlineVariant,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Nenhuma questão vinculada ainda.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Use "Buscar" para encontrar questões relacionadas.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outlineVariant,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            )
          else
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              sliver: SliverList.builder(
                itemCount: state.questionList.length,
                itemBuilder: (_, i) => QuestionListTile(
                  question: state.questionList[i],
                  index: i,
                ),
              ),
            ),

          // Seção de questões relacionadas (resultado do kNN)
          SliverToBoxAdapter(
            child: _RelatedQuestionsSection(state: state),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 100)),
        ],
      ),
      floatingActionButton: hasQuestions
          ? FloatingActionButton.extended(
              onPressed: () => context.go('/study-notes/$noteId/quiz'),
              icon: const Icon(Icons.play_arrow_rounded),
              label: const Text('Iniciar Simulado'),
            )
          : null,
    );
  }
}

class _NoteContent extends StatelessWidget {
  final dynamic note;

  const _NoteContent({required this.note});

  @override
  Widget build(BuildContext context) {
    final content = note.content as String?;
    final description = note.description as String?;

    if (content != null && content.isNotEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: MarkdownBody(
            data: content,
            styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)),
          ),
        ),
      );
    }

    if (description != null && description.isNotEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(description),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          'Nota sem conteúdo.',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
      ),
    );
  }
}

class _RelatedQuestionsSection extends StatelessWidget {
  final StudyNoteDetailState state;

  const _RelatedQuestionsSection({required this.state});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final relatedAsync = state.relatedQuestions;

    return relatedAsync.when(
      loading: () => const Padding(
        padding: EdgeInsets.all(24),
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Padding(
        padding: const EdgeInsets.all(16),
        child: Card(
          color: theme.colorScheme.errorContainer,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(Icons.error_outline,
                    color: theme.colorScheme.onErrorContainer),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    err is ApiException
                        ? err.firstMessage
                        : 'Erro ao buscar questões',
                    style: TextStyle(color: theme.colorScheme.onErrorContainer),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      data: (questions) {
        if (questions.isEmpty) return const SizedBox.shrink();

        return Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 16),
              Row(
                children: [
                  Text(
                    'Questões encontradas',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${questions.length}',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onPrimaryContainer,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ...questions.map((q) => RelatedQuestionCard(item: q)),
            ],
          ),
        );
      },
    );
  }
}
