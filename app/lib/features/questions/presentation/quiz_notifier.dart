import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../study_notes/presentation/study_note_detail_notifier.dart';
import '../data/questions_repository.dart';
import '../domain/question.dart';
import 'quiz_state.dart';

part 'quiz_notifier.g.dart';

@riverpod
class Quiz extends _$Quiz {
  @override
  QuizState build(String noteId) {
    // Lê a lista já carregada — sem nova requisição de rede
    final detailState = ref.watch(studyNoteDetailProvider(noteId));
    final questions = detailState.requireValue.questionList;

    return QuizState(
      questions: questions
          .map((q) => QuizQuestionState(question: q))
          .toList(),
    );
  }

  Future<void> submitAnswer(Alternative answer) async {
    final current = state.current;

    // Idempotência: ignora se já respondeu ou está verificando
    if (current.status != QuizAnswerStatus.unanswered) return;

    // Marca 'checking' sincronamente — bloqueia a UI imediatamente
    state = state.copyWith(
      questions: _updateCurrent(
        current.copyWith(
          status: QuizAnswerStatus.checking,
          selectedAnswer: answer,
        ),
      ),
    );

    try {
      final isCorrect = await ref
          .read(questionsRepositoryProvider)
          .checkAnswer(current.question.id, answer);

      state = state.copyWith(
        questions: _updateCurrent(
          state.current.copyWith(
            status: isCorrect ? QuizAnswerStatus.correct : QuizAnswerStatus.incorrect,
          ),
        ),
      );
    } catch (_) {
      // Reverte para unanswered para o usuário poder tentar novamente
      state = state.copyWith(
        questions: _updateCurrent(
          state.current.copyWith(
            status: QuizAnswerStatus.unanswered,
            selectedAnswer: null,
          ),
        ),
      );
      rethrow;
    }
  }

  void nextQuestion() {
    if (state.currentIndex < state.totalCount - 1) {
      state = state.copyWith(currentIndex: state.currentIndex + 1);
    } else {
      state = state.copyWith(isFinished: true);
    }
  }

  List<QuizQuestionState> _updateCurrent(QuizQuestionState updated) {
    final list = [...state.questions];
    list[state.currentIndex] = updated;
    return list;
  }
}
