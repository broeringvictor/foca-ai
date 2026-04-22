import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';

import '../router/navigator_key.dart';

// Sem import de router.dart — quebra a dependência circular:
// api_client → auth_interceptor → navigator_key (sem deps de feature)
class AuthInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 401) {
      final context = navigatorKey.currentContext;
      if (context != null) {
        GoRouter.of(context).go('/auth');
      }
    }
    handler.next(err);
  }
}
