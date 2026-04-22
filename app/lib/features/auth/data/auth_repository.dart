import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../domain/user.dart';
import 'auth_remote_data_source.dart';

part 'auth_repository.g.dart';

class AuthRepository {
  final AuthRemoteDataSource _dataSource;

  const AuthRepository(this._dataSource);

  Future<void> authenticate(String email, String password) =>
      _dataSource.authenticate(email, password);

  Future<User> getMe() async {
    final dto = await _dataSource.getMe();
    return User(
      userId: dto.userId,
      firstName: dto.name.firstName,
      lastName: dto.name.lastName,
      fullName: dto.name.value,
      email: dto.email,
      isActive: dto.isActive,
      createdAt: dto.createdAt,
      updatedAt: dto.updatedAt,
    );
  }
}

@Riverpod(keepAlive: true)
AuthRepository authRepository(AuthRepositoryRef ref) =>
    AuthRepository(ref.watch(authRemoteDataSourceProvider));
