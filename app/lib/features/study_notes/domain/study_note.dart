import 'package:freezed_annotation/freezed_annotation.dart';

import '../../questions/domain/question.dart';

part 'study_note.freezed.dart';

@freezed
class StudyNote with _$StudyNote {
  const factory StudyNote({
    required String id,
    required String title,
    String? description,
    @Default([]) List<String> tags,
    String? content,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _StudyNote;
}

// Projeção mínima da GET /question-list — sem gabarito
@freezed
class StudyNoteQuestionListItem with _$StudyNoteQuestionListItem {
  const factory StudyNoteQuestionListItem({
    required String id,
    required String statement,
    required String alternativeA,
    required String alternativeB,
    required String alternativeC,
    required String alternativeD,
  }) = _StudyNoteQuestionListItem;

  const StudyNoteQuestionListItem._();

  String alternativeText(Alternative alt) => switch (alt) {
        Alternative.A => alternativeA,
        Alternative.B => alternativeB,
        Alternative.C => alternativeC,
        Alternative.D => alternativeD,
      };
}

// Resultado da busca kNN (POST /questions)
@freezed
class RelatedQuestion with _$RelatedQuestion {
  const factory RelatedQuestion({
    required Question question,
    required double score,
  }) = _RelatedQuestion;
}
