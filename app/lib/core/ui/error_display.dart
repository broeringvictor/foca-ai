import 'package:flutter/material.dart';

import '../network/app_exception.dart';

class ErrorDisplay extends StatelessWidget {
  final AppException exception;
  final VoidCallback? onRetry;

  const ErrorDisplay({super.key, required this.exception, this.onRetry});

  String get _message => switch (exception) {
        ApiException e => e.firstMessage,
        NetworkException e => e.message,
        UnknownException _ => 'Ocorreu um erro inesperado',
      };

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              _message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 16),
              FilledButton.tonal(
                onPressed: onRetry,
                child: const Text('Tentar novamente'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
