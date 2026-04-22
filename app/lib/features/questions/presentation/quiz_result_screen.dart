import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'quiz_state.dart';

class QuizResultScreen extends StatelessWidget {
  final String noteId;
  final QuizState state;

  const QuizResultScreen({
    super.key,
    required this.noteId,
    required this.state,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final pct = state.totalCount > 0
        ? (state.correctCount / state.totalCount * 100).round()
        : 0;
    final color = pct >= 70 ? Colors.green : pct >= 50 ? Colors.orange : Colors.red;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Resultado'),
        automaticallyImplyLeading: false,
      ),
      body: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.15),
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '$pct%',
                        style: theme.textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '${state.correctCount} de ${state.totalCount} corretas',
                    style: theme.textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    pct >= 70
                        ? 'Ótimo resultado! Continue assim.'
                        : pct >= 50
                            ? 'Bom, mas há espaço para melhorar.'
                            : 'Continue praticando!',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 32),
                  FilledButton.icon(
                    onPressed: () => context.go('/study-notes/$noteId'),
                    icon: const Icon(Icons.arrow_back_rounded),
                    label: const Text('Voltar à nota'),
                  ),
                ],
              ),
            ),
          ),

          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList.builder(
              itemCount: state.questions.length,
              itemBuilder: (_, i) {
                final q = state.questions[i];
                final isCorrect = q.status == QuizAnswerStatus.correct;
                final color = isCorrect ? Colors.green : Colors.red;

                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: Icon(
                      isCorrect ? Icons.check_circle_rounded : Icons.cancel_rounded,
                      color: color,
                    ),
                    title: Text(
                      q.question.statement,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall,
                    ),
                    subtitle: q.selectedAnswer != null
                        ? Text(
                            'Respondeu: ${q.selectedAnswer!.name}',
                            style: TextStyle(color: color, fontSize: 12),
                          )
                        : const Text(
                            'Não respondida',
                            style: TextStyle(fontSize: 12),
                          ),
                  ),
                );
              },
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 32)),
        ],
      ),
    );
  }
}
