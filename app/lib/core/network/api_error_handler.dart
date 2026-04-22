import 'package:dio/dio.dart';

import 'app_exception.dart';
import 'error_dto.dart';

AppException handleDioException(DioException e) {
  final response = e.response;

  if (response != null) {
    try {
      final data = response.data;
      if (data is Map<String, dynamic>) {
        final errorResponse = ErrorResponse.fromJson(data);
        return ApiException(
          statusCode: response.statusCode!,
          errors: errorResponse.detail,
        );
      }
    } catch (_) {
      // fall through to generic api error
    }
    return ApiException(
      statusCode: response.statusCode ?? 0,
      errors: const [],
    );
  }

  if (e.type == DioExceptionType.connectionTimeout ||
      e.type == DioExceptionType.receiveTimeout ||
      e.type == DioExceptionType.sendTimeout) {
    return const NetworkException('Tempo de conexão esgotado');
  }

  if (e.type == DioExceptionType.connectionError) {
    return const NetworkException('Sem conexão com o servidor');
  }

  return UnknownException(e);
}
