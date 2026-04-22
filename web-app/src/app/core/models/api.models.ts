export type Alternative = 'A' | 'B' | 'C' | 'D';

export type LawArea =
  | 'direito_constitucional' | 'direitos_humanos' | 'etica_profissional'
  | 'filosofia_do_direito' | 'direito_internacional' | 'direito_tributario'
  | 'direito_administrativo' | 'direito_ambiental' | 'direito_civil'
  | 'direito_do_consumidor' | 'eca' | 'direito_empresarial' | 'direito_penal'
  | 'direito_processual_civil' | 'direito_processual_penal'
  | 'direito_do_trabalho' | 'direito_processual_do_trabalho'
  | 'direito_previdenciario' | 'direito_financeiro';

export interface AuthenticateDTO { email: string; password: string; }
export interface AuthenticateResponse { token: string; }

export interface UserName { first_name: string; last_name: string; value: string; }
export interface GetMeResponse {
  user_id: string; name: UserName; email: string;
  is_active: boolean; created_at: string; updated_at: string;
}

export interface RegisterDTO { first_name: string; last_name: string; email: string; password: string; password_confirm: string; }

export interface StudyNoteListItem { id: string; title: string; has_embedding: boolean; }
export interface ListStudyNotesResponse { items: StudyNoteListItem[]; }

export interface GetStudyNoteResponse {
  id: string;
  title: string;
  description: string | null;
  content: string | null;
  tags: string[];
  questions: string[];
  created_at: string;
  updated_at: string;
}

export interface Exam {
  id: string; name: string; edition: number; year: number; board: string;
  first_phase_date: string | null; second_phase_date: string | null;
  created_at: string; updated_at: string;
}
export interface ListExamsResponse { exams: Exam[]; }

export interface Question {
  id: string; exam_id: string; statement: string; area: LawArea;
  alternative_a: string; alternative_b: string;
  alternative_c: string; alternative_d: string;
  tags: string[]; created_at: string; updated_at: string;
}
export interface ListQuestionsResponse { questions: Question[]; }
export interface CheckAnswerDTO { answer: Alternative; }
export interface CheckAnswerResponse { question_id: string; is_correct: boolean; }

export interface ErrorItem { field: string; message: string; source?: string | null; }
export interface ErrorResponse { detail: ErrorItem[]; }
