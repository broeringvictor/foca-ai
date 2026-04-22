import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_error_handler.dart';
import '../domain/question.dart';
import 'question_dto.dart';

part 'questions_remote_data_source.g.dart';

class QuestionsRemoteDataSource {
  final Dio _dio;

  const QuestionsRemoteDataSource(this._dio);

  Future<bool> checkAnswer(String questionId, Alternative answer) async {
    try {
      final response = await _dio.post(
        '/api/v1/questions/$questionId/check',
        data: CheckAnswerRequest(answer: answer.name).toJson(),
      );
      return CheckAnswerResponseDto.fromJson(
        response.data as Map<String, dynamic>,
      ).isCorrect;
    } on DioException catch (e) {
      throw handleDioException(e);
    }
  }
}

@Riverpod(keepAlive: true)
QuestionsRemoteDataSource questionsRemoteDataSource(
        QuestionsRemoteDataSourceRef ref) =>
    QuestionsRemoteDataSource(ref.watch(apiClientProvider));
