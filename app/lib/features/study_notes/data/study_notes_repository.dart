import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../questions/domain/question.dart';
import '../domain/study_note.dart';
import 'study_notes_remote_data_source.dart';

part 'study_notes_repository.g.dart';

class StudyNotesRepository {
  final StudyNotesRemoteDataSource _dataSource;

  const StudyNotesRepository(this._dataSource);

  Future<StudyNote> getStudyNote(String studyNoteId) async {
    final dto = await _dataSource.getStudyNote(studyNoteId);
    return StudyNote(
      id: dto.id,
      title: dto.title,
      description: dto.description,
      tags: dto.tags ?? [],
      content: dto.content,
      createdAt: dto.createdAt,
      updatedAt: dto.updatedAt,
    );
  }

  Future<List<StudyNoteQuestionListItem>> getQuestionList(
      String studyNoteId) async {
    final dto = await _dataSource.getQuestionList(studyNoteId);
    return dto.questions
        .map(
          (q) => StudyNoteQuestionListItem(
            id: q.id,
            statement: q.statement,
            alternativeA: q.alternativeA,
            alternativeB: q.alternativeB,
            alternativeC: q.alternativeC,
            alternativeD: q.alternativeD,
          ),
        )
        .toList();
  }

  Future<List<RelatedQuestion>> findRelatedQuestions(
    String studyNoteId, {
    required int limit,
    String? examId,
  }) async {
    final dto = await _dataSource.findRelatedQuestions(
      studyNoteId,
      limit: limit,
      examId: examId,
    );
    return (dto.items ?? [])
        .map(
          (item) => RelatedQuestion(
            score: item.score,
            question: Question(
              id: item.question.id,
              examId: item.question.examId,
              statement: item.question.statement,
              area: LawArea.fromJson(item.question.area),
              alternativeA: item.question.alternativeA,
              alternativeB: item.question.alternativeB,
              alternativeC: item.question.alternativeC,
              alternativeD: item.question.alternativeD,
              tags: item.question.tags,
              createdAt: item.question.createdAt,
              updatedAt: item.question.updatedAt,
            ),
          ),
        )
        .toList();
  }
}

@Riverpod(keepAlive: true)
StudyNotesRepository studyNotesRepository(StudyNotesRepositoryRef ref) =>
    StudyNotesRepository(ref.watch(studyNotesRemoteDataSourceProvider));
