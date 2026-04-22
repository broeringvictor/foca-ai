import 'package:flutter/material.dart';

import '../../domain/question.dart';
import '../quiz_state.dart';

class AnswerOptionTile extends StatelessWidget {
  final Alternative alternative;
  final String text;
  final QuizAnswerStatus status;
  final Alternative? selectedAnswer;
  final VoidCallback? onTap;

  const AnswerOptionTile({
    super.key,
    required this.alternative,
    required this.text,
    required this.status,
    required this.selectedAnswer,
    this.onTap,
  });

  bool get _isSelected => selectedAnswer == alternative;

  Color? _backgroundColor(BuildContext context) {
    if (!_isSelected) return null;
    return switch (status) {
      QuizAnswerStatus.correct => Colors.green.shade100,
      QuizAnswerStatus.incorrect => Colors.red.shade100,
      _ => null,
    };
  }

  Color? _borderColor(BuildContext context) {
    if (!_isSelected) return null;
    return switch (status) {
      QuizAnswerStatus.correct => Colors.green,
      QuizAnswerStatus.incorrect => Colors.red,
      _ => Theme.of(context).colorScheme.primary,
    };
  }

  IconData? get _trailingIcon {
    if (!_isSelected) return null;
    return switch (status) {
      QuizAnswerStatus.correct => Icons.check_circle_rounded,
      QuizAnswerStatus.incorrect => Icons.cancel_rounded,
      _ => null,
    };
  }

  Color? _trailingColor(BuildContext context) {
    return switch (status) {
      QuizAnswerStatus.correct => Colors.green,
      QuizAnswerStatus.incorrect => Colors.red,
      _ => null,
    };
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isAnswered = status != QuizAnswerStatus.unanswered &&
        status != QuizAnswerStatus.checking;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        decoration: BoxDecoration(
          color: _backgroundColor(context) ??
              theme.colorScheme.surfaceContainerHighest.withOpacity(0.4),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: _borderColor(context) ?? theme.colorScheme.outlineVariant,
            width: _isSelected ? 2 : 1,
          ),
        ),
        child: ListTile(
          onTap: isAnswered ? null : onTap,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          leading: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: _isSelected
                  ? (_borderColor(context) ?? theme.colorScheme.primary)
                  : theme.colorScheme.surfaceContainerHighest,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                alternative.name,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: _isSelected
                      ? Colors.white
                      : theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ),
          title: Text(
            text,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: isAnswered && !_isSelected
                  ? theme.colorScheme.onSurfaceVariant.withOpacity(0.6)
                  : null,
            ),
          ),
          trailing: _trailingIcon != null
              ? Icon(_trailingIcon, color: _trailingColor(context))
              : null,
        ),
      ),
    );
  }
}
