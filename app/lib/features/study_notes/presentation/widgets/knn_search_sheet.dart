import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../study_note_detail_notifier.dart';

class KnnSearchSheet extends ConsumerWidget {
  final String noteId;

  const KnnSearchSheet({super.key, required this.noteId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studyNoteDetailProvider(noteId)).requireValue;
    final notifier = ref.read(studyNoteDetailProvider(noteId).notifier);
    final theme = Theme.of(context);

    return Padding(
      padding: EdgeInsets.fromLTRB(
        24,
        24,
        24,
        MediaQuery.viewInsetsOf(context).bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Buscar questões relacionadas',
            style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'Busca questões semanticamente similares à sua nota usando embeddings.',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Text('Quantidade:', style: theme.textTheme.bodyMedium),
              const SizedBox(width: 16),
              Expanded(
                child: DropdownButtonFormField<int>(
                  value: state.knnLimit,
                  decoration: const InputDecoration(
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  items: [3, 5, 10, 15, 20]
                      .map(
                        (v) => DropdownMenuItem(value: v, child: Text('$v questões')),
                      )
                      .toList(),
                  onChanged: (v) {
                    if (v != null) notifier.setLimit(v);
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () {
              Navigator.pop(context);
              notifier.findRelatedQuestions();
            },
            icon: const Icon(Icons.search_rounded),
            label: const Text('Buscar'),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
        ],
      ),
    );
  }
}
