import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/study_notes_repository.dart';
import '../domain/study_note.dart';

part 'study_note_detail_notifier.freezed.dart';
part 'study_note_detail_notifier.g.dart';

@freezed
class StudyNoteDetailState with _$StudyNoteDetailState {
  const factory StudyNoteDetailState({
    required StudyNote note,
    required List<StudyNoteQuestionListItem> questionList,
    @Default(AsyncValue<List<RelatedQuestion>>.data([]))
    AsyncValue<List<RelatedQuestion>> relatedQuestions,
    @Default(5) int knnLimit,
    String? selectedExamId,
  }) = _StudyNoteDetailState;
}

@riverpod
class StudyNoteDetail extends _$StudyNoteDetail {
  @override
  Future<StudyNoteDetailState> build(String noteId) async {
    final repo = ref.watch(studyNotesRepositoryProvider);

    // Busca nota e lista de questões em paralelo
    final results = await Future.wait([
      repo.getStudyNote(noteId),
      repo.getQuestionList(noteId),
    ]);

    return StudyNoteDetailState(
      note: results[0] as StudyNote,
      questionList: results[1] as List<StudyNoteQuestionListItem>,
    );
  }

  Future<void> findRelatedQuestions() async {
    final current = state.requireValue;
    state = AsyncData(
      current.copyWith(relatedQuestions: const AsyncLoading()),
    );

    final result = await AsyncValue.guard(
      () => ref.read(studyNotesRepositoryProvider).findRelatedQuestions(
            noteId,
            limit: current.knnLimit,
            examId: current.selectedExamId,
          ),
    );

    state = AsyncData(state.requireValue.copyWith(relatedQuestions: result));
  }

  Future<void> refreshQuestionList() async {
    final current = state.requireValue;
    final questions = await ref
        .read(studyNotesRepositoryProvider)
        .getQuestionList(noteId);
    state = AsyncData(current.copyWith(questionList: questions));
  }

  void setLimit(int limit) {
    final current = state.requireValue;
    state = AsyncData(current.copyWith(knnLimit: limit));
  }

  void setExamId(String? examId) {
    final current = state.requireValue;
    state = AsyncData(current.copyWith(selectedExamId: examId));
  }
}
