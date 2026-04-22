import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/presentation/auth_state_notifier.dart';

class StudyNotesHomeScreen extends ConsumerStatefulWidget {
  const StudyNotesHomeScreen({super.key});

  @override
  ConsumerState<StudyNotesHomeScreen> createState() =>
      _StudyNotesHomeScreenState();
}

class _StudyNotesHomeScreenState extends ConsumerState<StudyNotesHomeScreen> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _navigate() {
    final id = _controller.text.trim();
    if (id.isNotEmpty) {
      context.go('/study-notes/$id');
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authStateProvider).valueOrNull;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('FocaAI'),
        actions: [
          if (user != null)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: TextButton.icon(
                onPressed: () => ref.read(authStateProvider.notifier).logout(),
                icon: const Icon(Icons.logout_rounded, size: 18),
                label: Text(user.firstName),
              ),
            ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Icon(
                  Icons.school_rounded,
                  size: 64,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 24),
                Text(
                  'Bem-vindo${user != null ? ', ${user.firstName}' : ''}!',
                  style: theme.textTheme.headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Acesse uma nota de estudo pelo seu ID para começar.',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                TextField(
                  controller: _controller,
                  decoration: const InputDecoration(
                    labelText: 'ID da nota de estudo',
                    hintText: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                    prefixIcon: Icon(Icons.notes_rounded),
                  ),
                  onSubmitted: (_) => _navigate(),
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: _navigate,
                  icon: const Icon(Icons.arrow_forward_rounded),
                  label: const Text('Abrir nota'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
