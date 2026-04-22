import 'error_dto.dart';

sealed class AppException implements Exception {
  const AppException();
}

class ApiException extends AppException {
  final int statusCode;
  final List<ErrorItem> errors;

  const ApiException({required this.statusCode, required this.errors});

  String get firstMessage =>
      errors.firstOrNull?.message ?? 'Erro desconhecido';

  @override
  String toString() => 'ApiException($statusCode): $firstMessage';
}

class NetworkException extends AppException {
  final String message;

  const NetworkException(this.message);

  @override
  String toString() => 'NetworkException: $message';
}

class UnknownException extends AppException {
  final Object cause;

  const UnknownException(this.cause);

  @override
  String toString() => 'UnknownException: $cause';
}
