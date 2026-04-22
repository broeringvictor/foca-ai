import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/network/app_exception.dart';
import '../../../core/ui/loading_overlay.dart';
import '../domain/question.dart';
import 'quiz_notifier.dart';
import 'quiz_result_screen.dart';
import 'quiz_state.dart';
import 'widgets/answer_option_tile.dart';

class StudyNoteQuizScreen extends ConsumerWidget {
  final String noteId;

  const StudyNoteQuizScreen({super.key, required this.noteId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(quizProvider(noteId));

    ref.listen(quizProvider(noteId), (prev, next) {
      // Detecta erro comparando com estado anterior
      // O notifier relança exceções após reverter o estado
    });

    if (state.isFinished) {
      return QuizResultScreen(noteId: noteId, state: state);
    }

    final current = state.current;
    final isChecking = current.status == QuizAnswerStatus.checking;
    final isAnswered = current.status == QuizAnswerStatus.correct ||
        current.status == QuizAnswerStatus.incorrect;
    final notifier = ref.read(quizProvider(noteId).notifier);

    return Scaffold(
      appBar: AppBar(
        leading: BackButton(onPressed: () => context.pop()),
        title: Text('${state.currentIndex + 1} / ${state.totalCount}'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(
                '${state.correctCount} ✓',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(
            value: state.progress,
            backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
          ),
        ),
      ),
      body: LoadingOverlay(
        isLoading: isChecking,
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Enunciado
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          current.question.statement,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Feedback de resposta
                    if (isAnswered) _AnswerFeedback(status: current.status),
                    if (isAnswered) const SizedBox(height: 16),

                    // Alternativas
                    ...Alternative.values.map(
                      (alt) => AnswerOptionTile(
                        alternative: alt,
                        text: current.question.alternativeText(alt),
                        status: current.status,
                        selectedAnswer: current.selectedAnswer,
                        onTap: isAnswered || isChecking
                            ? null
                            : () => _submitAnswer(context, ref, alt),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Botão próxima
            if (isAnswered)
              SafeArea(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                  child: FilledButton.icon(
                    onPressed: notifier.nextQuestion,
                    icon: Icon(
                      state.currentIndex < state.totalCount - 1
                          ? Icons.arrow_forward_rounded
                          : Icons.check_rounded,
                    ),
                    label: Text(
                      state.currentIndex < state.totalCount - 1
                          ? 'Próxima questão'
                          : 'Ver resultado',
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _submitAnswer(
    BuildContext context,
    WidgetRef ref,
    Alternative answer,
  ) async {
    try {
      await ref.read(quizProvider(noteId).notifier).submitAnswer(answer);
    } on AppException catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e is ApiException ? e.firstMessage : 'Erro ao verificar resposta',
            ),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }
}

class _AnswerFeedback extends StatelessWidget {
  final QuizAnswerStatus status;

  const _AnswerFeedback({required this.status});

  @override
  Widget build(BuildContext context) {
    final isCorrect = status == QuizAnswerStatus.correct;
    final color = isCorrect ? Colors.green : Colors.red;
    final icon = isCorrect ? Icons.check_circle_rounded : Icons.cancel_rounded;
    final text = isCorrect ? 'Resposta correta!' : 'Resposta incorreta';

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 12),
          Text(
            text,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
