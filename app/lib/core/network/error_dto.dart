import 'package:json_annotation/json_annotation.dart';

part 'error_dto.g.dart';

@JsonSerializable()
class ErrorItem {
  final String field;
  final String message;
  final String? source;

  const ErrorItem({
    required this.field,
    required this.message,
    this.source,
  });

  factory ErrorItem.fromJson(Map<String, dynamic> json) =>
      _$ErrorItemFromJson(json);
}

@JsonSerializable()
class ErrorResponse {
  final List<ErrorItem> detail;

  const ErrorResponse({required this.detail});

  factory ErrorResponse.fromJson(Map<String, dynamic> json) =>
      _$ErrorResponseFromJson(json);
}
