import 'package:json_annotation/json_annotation.dart';

import '../../questions/data/question_dto.dart';

part 'study_notes_dto.g.dart';

@JsonSerializable()
class StudyNoteDto {
  final String id;
  final String title;
  final String? description;
  final List<String>? tags;
  final String? content;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  const StudyNoteDto({
    required this.id,
    required this.title,
    this.description,
    this.tags,
    this.content,
    required this.createdAt,
    required this.updatedAt,
  });

  factory StudyNoteDto.fromJson(Map<String, dynamic> json) =>
      _$StudyNoteDtoFromJson(json);
}

@JsonSerializable()
class QuestionListItemDto {
  final String id;
  final String statement;

  @JsonKey(name: 'alternative_a')
  final String alternativeA;

  @JsonKey(name: 'alternative_b')
  final String alternativeB;

  @JsonKey(name: 'alternative_c')
  final String alternativeC;

  @JsonKey(name: 'alternative_d')
  final String alternativeD;

  const QuestionListItemDto({
    required this.id,
    required this.statement,
    required this.alternativeA,
    required this.alternativeB,
    required this.alternativeC,
    required this.alternativeD,
  });

  factory QuestionListItemDto.fromJson(Map<String, dynamic> json) =>
      _$QuestionListItemDtoFromJson(json);
}

@JsonSerializable()
class GetQuestionsListResponseDto {
  final List<QuestionListItemDto> questions;

  const GetQuestionsListResponseDto({required this.questions});

  factory GetQuestionsListResponseDto.fromJson(Map<String, dynamic> json) =>
      _$GetQuestionsListResponseDtoFromJson(json);
}

@JsonSerializable()
class RelatedQuestionItemDto {
  final GetQuestionResponseDto question;
  final double score;

  const RelatedQuestionItemDto({required this.question, required this.score});

  factory RelatedQuestionItemDto.fromJson(Map<String, dynamic> json) =>
      _$RelatedQuestionItemDtoFromJson(json);
}

@JsonSerializable()
class FindRelatedQuestionsToNoteResponseDto {
  @JsonKey(name: 'study_note_id')
  final String studyNoteId;

  final List<RelatedQuestionItemDto>? items;

  const FindRelatedQuestionsToNoteResponseDto({
    required this.studyNoteId,
    this.items,
  });

  factory FindRelatedQuestionsToNoteResponseDto.fromJson(
          Map<String, dynamic> json) =>
      _$FindRelatedQuestionsToNoteResponseDtoFromJson(json);
}
