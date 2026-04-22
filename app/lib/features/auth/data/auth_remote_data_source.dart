import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_error_handler.dart';
import 'auth_dto.dart';

part 'auth_remote_data_source.g.dart';

class AuthRemoteDataSource {
  final Dio _dio;

  const AuthRemoteDataSource(this._dio);

  Future<void> authenticate(String email, String password) async {
    try {
      await _dio.post(
        '/api/v1/auth/authenticate',
        data: AuthenticateRequest(email: email, password: password).toJson(),
      );
    } on DioException catch (e) {
      throw handleDioException(e);
    }
  }

  Future<GetMeResponseDto> getMe() async {
    try {
      final response = await _dio.get('/api/v1/users/me');
      return GetMeResponseDto.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleDioException(e);
    }
  }
}

@Riverpod(keepAlive: true)
AuthRemoteDataSource authRemoteDataSource(AuthRemoteDataSourceRef ref) =>
    AuthRemoteDataSource(ref.watch(apiClientProvider));
