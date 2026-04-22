import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';

@freezed
class User with _$User {
  const factory User({
    required String userId,
    required String firstName,
    required String lastName,
    required String fullName,
    required String email,
    required bool isActive,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _User;
}
