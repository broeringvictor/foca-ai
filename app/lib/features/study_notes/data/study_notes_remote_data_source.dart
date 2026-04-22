import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_error_handler.dart';
import 'study_notes_dto.dart';

part 'study_notes_remote_data_source.g.dart';

class StudyNotesRemoteDataSource {
  final Dio _dio;

  const StudyNotesRemoteDataSource(this._dio);

  Future<StudyNoteDto> getStudyNote(String studyNoteId) async {
    try {
      final response = await _dio.get('/api/v1/study-notes/$studyNoteId');
      return StudyNoteDto.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleDioException(e);
    }
  }

  Future<GetQuestionsListResponseDto> getQuestionList(String studyNoteId) async {
    try {
      final response = await _dio.get(
        '/api/v1/study-notes/$studyNoteId/question-list',
      );
      return GetQuestionsListResponseDto.fromJson(
        response.data as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw handleDioException(e);
    }
  }

  Future<FindRelatedQuestionsToNoteResponseDto> findRelatedQuestions(
    String studyNoteId, {
    required int limit,
    String? examId,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/study-notes/$studyNoteId/questions',
        queryParameters: {
          'limit': limit,
          if (examId != null) 'exam_id': examId,
        },
      );
      return FindRelatedQuestionsToNoteResponseDto.fromJson(
        response.data as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw handleDioException(e);
    }
  }
}

@Riverpod(keepAlive: true)
StudyNotesRemoteDataSource studyNotesRemoteDataSource(
        StudyNotesRemoteDataSourceRef ref) =>
    StudyNotesRemoteDataSource(ref.watch(apiClientProvider));
