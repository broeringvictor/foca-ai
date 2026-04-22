import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../features/auth/presentation/auth_screen.dart';
import '../../features/auth/presentation/auth_state_notifier.dart';
import '../../features/questions/presentation/quiz_screen.dart';
import '../../features/study_notes/presentation/study_note_detail_screen.dart';
import '../../features/study_notes/presentation/study_notes_home_screen.dart';
import 'navigator_key.dart';

part 'router.g.dart';

@Riverpod(keepAlive: true)
GoRouter router(RouterRef ref) {
  // ChangeNotifier que notifica o GoRouter quando o auth muda
  final notifier = _AuthStateChangeNotifier(ref);

  return GoRouter(
    navigatorKey: navigatorKey,
    initialLocation: '/auth',
    refreshListenable: notifier,
    redirect: (context, state) {
      final authAsync = notifier.authState;

      if (authAsync.isLoading) return null;

      final isAuthenticated = authAsync.valueOrNull != null;
      final onAuth = state.matchedLocation == '/auth';

      if (!isAuthenticated && !onAuth) return '/auth';
      if (isAuthenticated && onAuth) return '/study-notes';
      return null;
    },
    routes: [
      GoRoute(
        path: '/auth',
        name: 'auth',
        builder: (_, __) => const AuthScreen(),
      ),
      GoRoute(
        path: '/study-notes',
        name: 'study-notes-home',
        builder: (_, __) => const StudyNotesHomeScreen(),
      ),
      GoRoute(
        path: '/study-notes/:id',
        name: 'study-note-detail',
        builder: (_, state) => StudyNoteDetailScreen(
          noteId: state.pathParameters['id']!,
        ),
        routes: [
          GoRoute(
            path: 'quiz',
            name: 'quiz',
            builder: (_, state) => StudyNoteQuizScreen(
              noteId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
    ],
  );
}

class _AuthStateChangeNotifier extends ChangeNotifier {
  final RouterRef _ref;
  late AsyncValue _prev;

  _AuthStateChangeNotifier(this._ref) {
    _prev = _ref.read(authStateProvider);
    _ref.listen(authStateProvider, (prev, next) {
      if (prev != next) notifyListeners();
    });
  }

  AsyncValue get authState => _ref.read(authStateProvider);
}
