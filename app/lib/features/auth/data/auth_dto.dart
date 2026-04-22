import 'package:json_annotation/json_annotation.dart';

part 'auth_dto.g.dart';

@JsonSerializable()
class AuthenticateRequest {
  final String email;
  final String password;

  const AuthenticateRequest({required this.email, required this.password});

  Map<String, dynamic> toJson() => _$AuthenticateRequestToJson(this);
}

@JsonSerializable()
class AuthenticateResponse {
  final String token;

  const AuthenticateResponse({required this.token});

  factory AuthenticateResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthenticateResponseFromJson(json);
}

@JsonSerializable()
class NameDto {
  @JsonKey(name: 'first_name')
  final String firstName;

  @JsonKey(name: 'last_name')
  final String lastName;

  final String value;

  const NameDto({
    required this.firstName,
    required this.lastName,
    required this.value,
  });

  factory NameDto.fromJson(Map<String, dynamic> json) =>
      _$NameDtoFromJson(json);
}

@JsonSerializable()
class GetMeResponseDto {
  @JsonKey(name: 'user_id')
  final String userId;

  final NameDto name;
  final String email;

  @JsonKey(name: 'is_active')
  final bool isActive;

  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  const GetMeResponseDto({
    required this.userId,
    required this.name,
    required this.email,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory GetMeResponseDto.fromJson(Map<String, dynamic> json) =>
      _$GetMeResponseDtoFromJson(json);
}
