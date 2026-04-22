import 'package:json_annotation/json_annotation.dart';

part 'question_dto.g.dart';

@JsonSerializable()
class GetQuestionResponseDto {
  final String id;

  @JsonKey(name: 'exam_id')
  final String examId;

  final String statement;
  final String area;

  @JsonKey(name: 'alternative_a')
  final String alternativeA;

  @JsonKey(name: 'alternative_b')
  final String alternativeB;

  @JsonKey(name: 'alternative_c')
  final String alternativeC;

  @JsonKey(name: 'alternative_d')
  final String alternativeD;

  final List<String> tags;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  const GetQuestionResponseDto({
    required this.id,
    required this.examId,
    required this.statement,
    required this.area,
    required this.alternativeA,
    required this.alternativeB,
    required this.alternativeC,
    required this.alternativeD,
    required this.tags,
    required this.createdAt,
    required this.updatedAt,
  });

  factory GetQuestionResponseDto.fromJson(Map<String, dynamic> json) =>
      _$GetQuestionResponseDtoFromJson(json);
}

@JsonSerializable()
class CheckAnswerRequest {
  final String answer;

  const CheckAnswerRequest({required this.answer});

  Map<String, dynamic> toJson() => _$CheckAnswerRequestToJson(this);
}

@JsonSerializable()
class CheckAnswerResponseDto {
  @JsonKey(name: 'question_id')
  final String questionId;

  @JsonKey(name: 'is_correct')
  final bool isCorrect;

  const CheckAnswerResponseDto({
    required this.questionId,
    required this.isCorrect,
  });

  factory CheckAnswerResponseDto.fromJson(Map<String, dynamic> json) =>
      _$CheckAnswerResponseDtoFromJson(json);
}
