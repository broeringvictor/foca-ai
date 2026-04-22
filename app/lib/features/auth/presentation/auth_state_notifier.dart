import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/network/app_exception.dart';
import '../data/auth_repository.dart';
import '../domain/user.dart';

part 'auth_state_notifier.g.dart';

@Riverpod(keepAlive: true)
class AuthState extends _$AuthState {
  @override
  Future<User?> build() async {
    try {
      return await ref.read(authRepositoryProvider).getMe();
    } on ApiException catch (e) {
      if (e.statusCode == 401 || e.statusCode == 400) return null;
      rethrow;
    } on NetworkException catch (_) {
      return null;
    }
  }

  Future<void> login(String email, String password) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(authRepositoryProvider).authenticate(email, password);
      return ref.read(authRepositoryProvider).getMe();
    });
  }

  void logout() {
    state = const AsyncData(null);
  }
}
