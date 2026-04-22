import 'package:freezed_annotation/freezed_annotation.dart';

import '../../study_notes/domain/study_note.dart';
import '../domain/question.dart';

part 'quiz_state.freezed.dart';

enum QuizAnswerStatus { unanswered, checking, correct, incorrect }

@freezed
class QuizQuestionState with _$QuizQuestionState {
  const factory QuizQuestionState({
    required StudyNoteQuestionListItem question,
    @Default(QuizAnswerStatus.unanswered) QuizAnswerStatus status,
    Alternative? selectedAnswer,
  }) = _QuizQuestionState;
}

@freezed
class QuizState with _$QuizState {
  const factory QuizState({
    required List<QuizQuestionState> questions,
    @Default(0) int currentIndex,
    @Default(false) bool isFinished,
  }) = _QuizState;

  const QuizState._();

  QuizQuestionState get current => questions[currentIndex];
  int get totalCount => questions.length;
  int get correctCount =>
      questions.where((q) => q.status == QuizAnswerStatus.correct).length;
  double get progress =>
      totalCount == 0 ? 0 : (currentIndex + 1) / totalCount;
}
