import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../domain/question.dart';
import 'questions_remote_data_source.dart';

part 'questions_repository.g.dart';

class QuestionsRepository {
  final QuestionsRemoteDataSource _dataSource;

  const QuestionsRepository(this._dataSource);

  Future<bool> checkAnswer(String questionId, Alternative answer) =>
      _dataSource.checkAnswer(questionId, answer);
}

@Riverpod(keepAlive: true)
QuestionsRepository questionsRepository(QuestionsRepositoryRef ref) =>
    QuestionsRepository(ref.watch(questionsRemoteDataSourceProvider));
