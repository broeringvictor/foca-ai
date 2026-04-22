import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/network/cookie_jar_provider.dart';
import 'core/router/router.dart';
import 'core/ui/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Pré-aquece o CookieJar no native para que apiClientProvider seja síncrono
  final container = ProviderContainer();
  if (!kIsWeb) {
    await container.read(cookieJarProvider.future);
  }

  runApp(
    UncontrolledProviderScope(
      container: container,
      child: const App(),
    ),
  );
}

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'FocaAI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      routerConfig: router,
    );
  }
}
