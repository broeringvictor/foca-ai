# Implementation Prompt — Auth, Study Notes & Quiz Screens

Follow all rules in `CLAUDE.md` throughout. Run `ng build` after finishing and fix all errors before reporting done.

---

## 1. TypeScript Models

Create `src/app/core/models/api.models.ts` with all types derived from the OpenAPI spec:

```ts
export type Alternative = 'A' | 'B' | 'C' | 'D';

export type LawArea =
  | 'direito_constitucional' | 'direitos_humanos' | 'etica_profissional'
  | 'filosofia_do_direito' | 'direito_internacional' | 'direito_tributario'
  | 'direito_administrativo' | 'direito_ambiental' | 'direito_civil'
  | 'direito_do_consumidor' | 'eca' | 'direito_empresarial' | 'direito_penal'
  | 'direito_processual_civil' | 'direito_processual_penal'
  | 'direito_do_trabalho' | 'direito_processual_do_trabalho'
  | 'direito_previdenciario' | 'direito_financeiro';

// Auth
export interface AuthenticateDTO { email: string; password: string; }
export interface AuthenticateResponse { token: string; }

// User
export interface UserName { first_name: string; last_name: string; value: string; }
export interface GetMeResponse {
  user_id: string; name: UserName; email: string;
  is_active: boolean; created_at: string; updated_at: string;
}

// Study Notes
export interface StudyNoteListItem { id: string; title: string; has_embedding: boolean; }
export interface ListStudyNotesResponse { items: StudyNoteListItem[]; }

// Exams
export interface Exam {
  id: string; name: string; edition: number; year: number; board: string;
  first_phase_date: string | null; second_phase_date: string | null;
  created_at: string; updated_at: string;
}
export interface ListExamsResponse { exams: Exam[]; }

// Questions
export interface Question {
  id: string; exam_id: string; statement: string; area: LawArea;
  alternative_a: string; alternative_b: string;
  alternative_c: string; alternative_d: string;
  tags: string[]; created_at: string; updated_at: string;
}
export interface ListQuestionsResponse { questions: Question[]; }
export interface CheckAnswerDTO { answer: Alternative; }
export interface CheckAnswerResponse { question_id: string; is_correct: boolean; }

// Errors
export interface ErrorItem { field: string; message: string; source?: string | null; }
export interface ErrorResponse { detail: ErrorItem[]; }
```

---

## 2. Core Infrastructure

### 2a. Environment / Base URL

Create `src/environments/environment.ts`:
```ts
export const environment = { apiUrl: 'http://localhost:8000' };
```

### 2b. HTTP Interceptor (credentials + 401 redirect)

Create `src/app/core/http/api.interceptor.ts` as a functional interceptor:

- Clone every request adding `withCredentials: true` and the full base URL prefix (`environment.apiUrl`) if the request URL starts with `/api`.
- On HTTP 401 response, inject `Router` and navigate to `/auth`.

Register it in `app.config.ts` via `provideHttpClient(withInterceptors([apiInterceptor]))`.

### 2c. Auth Service

Create `src/app/core/auth/auth.service.ts` (`providedIn: 'root'`):

```ts
// Fields
private _currentUser = signal<GetMeResponse | null>(null);
readonly currentUser = this._currentUser.asReadonly();
readonly isAuthenticated = computed(() => this._currentUser() !== null);

// Methods (all return Observables / Promises via HttpClient)
login(dto: AuthenticateDTO): Observable<AuthenticateResponse>
  // POST /api/v1/auth/authenticate
  // On success: call loadCurrentUser()

loadCurrentUser(): Observable<GetMeResponse>
  // GET /api/v1/users/me
  // On success: set _currentUser signal

logout(): void
  // Clear _currentUser signal and navigate to /auth
```

Call `authService.loadCurrentUser()` in `APP_INITIALIZER` (in `app.config.ts`) so the user state is restored on page refresh. Swallow errors (unauthenticated startup is valid).

### 2d. Auth Guard

Create `src/app/core/auth/auth.guard.ts` as `CanMatchFn`:
- If `authService.isAuthenticated()` → allow.
- Else → redirect to `/auth`.

---

## 3. Routing

`src/app/app.routes.ts`:

```ts
export const routes: Routes = [
  { path: '', redirectTo: 'study-notes', pathMatch: 'full' },
  {
    path: 'auth',
    loadComponent: () => import('./features/auth/auth.component'),
  },
  {
    path: 'study-notes',
    canMatch: [authGuard],
    loadChildren: () => import('./features/study-notes/study-notes.routes'),
  },
  { path: '**', redirectTo: 'study-notes' },
];
```

`src/app/features/study-notes/study-notes.routes.ts`:

```ts
export default [
  { path: '', loadComponent: () => import('./components/study-notes-list/study-notes-list.component') },
  { path: ':id', loadComponent: () => import('./components/study-note-detail/study-note-detail.component') },
  {
    path: ':id/quiz',
    loadComponent: () => import('./components/quiz/quiz.component'),
  },
] satisfies Routes;
```

---

## 4. Feature: Auth

**File:** `src/app/features/auth/auth.component.ts` + `auth.component.html`

### Behavior
- Single screen with a centered card (PrimeNG `Card`).
- Two tabs (PrimeNG `Tabs`): **Entrar** (login) and **Criar conta** (register).
- After successful login, navigate to `/study-notes`.

### Login tab — Signal Form

Model:
```ts
loginModel = signal({ email: '', password: '' });
loginForm = form(loginModel, (s) => {
  required(s.email); email(s.email, { message: 'E-mail inválido' });
  required(s.password, { message: 'Senha obrigatória' });
});
```

On submit: call `authService.login(loginModel())`. On `ErrorResponse` (HTTP 400), show `detail[0].message` via PrimeNG `Toast`.

### Register tab — Signal Form

Model:
```ts
registerModel = signal({ first_name: '', last_name: '', email: '', password: '', password_confirm: '' });
```

Validators: all fields `required`, `email()` on email, `minLength(s.password, 8)`, custom `validate` to confirm passwords match.

Call `POST /api/v1/users/` on submit. On 409 (email já cadastrado) show error toast. On success, switch to login tab.

### PrimeNG components to use
`Card`, `Tabs`, `Tab`, `TabList`, `TabPanel`, `InputText`, `Password`, `Button`, `Toast`.

---

## 5. Feature: Study Notes

### 5a. Study Notes List

**File:** `src/app/features/study-notes/components/study-notes-list/study-notes-list.component.ts`

Use `resource()` to fetch `GET /api/v1/study-notes/`:
```ts
readonly notes = resource({
  loader: () => this.studyNotesService.list(),
});
```

Template:
- Loading state: show PrimeNG `Skeleton` cards.
- Error state: show PrimeNG `Message` with a retry button (`notes.reload()`).
- List: PrimeNG `DataView` or a grid of PrimeNG `Card` components.
  - Each card shows `title` and a badge "Com embedding" if `has_embedding` is true.
  - Click navigates to `/study-notes/:id`.

### 5b. Study Note Detail

**File:** `src/app/features/study-notes/components/study-note-detail/study-note-detail.component.ts`

Read `:id` from route via `inject(ActivatedRoute).snapshot.paramMap.get('id')` (as a `signal`).

**⚠️ API Gap:** `GET /api/v1/study-notes/{id}` is not in the current spec. While it is not available, display the note title from the list (passed via router state or re-fetching the list and finding by id). Show a placeholder for the content body. Add a `TODO: awaiting GET /api/v1/study-notes/:id endpoint` comment.

**Layout — two panels side by side (Tailwind `grid grid-cols-2 gap-4`):**

**Left panel — Note content:**
- Note title as heading.
- Content area (placeholder text until detail endpoint is available).

**Right panel — Search questions:**

Two sub-sections:

**Section A — Search by exam:**
- PrimeNG `Select` (dropdown) populated from `GET /api/v1/exams/` listing all exams. Display as `{name} — {edition}ª ed. ({year})`.
- "Buscar questões" button: on click, load `GET /api/v1/questions/exam/{exam_id}` and display results below.
- Results: list of question statement previews with a "Adicionar ao estudo" button per question.
- **⚠️ API Gap:** "search by note content" (semantic search using `has_embedding`) has no endpoint in the current spec. Render the exam-filter search only, and add a `TODO: semantic search endpoint pending` comment where the content-search UI would go.

**Section B — Saved questions:**
- **⚠️ API Gap:** No endpoint to list questions linked to a study note exists in the spec. Render an empty state placeholder with a `TODO: GET /api/v1/study-notes/:id/questions pending` comment.

**"Estudar questões" button** (prominent, PrimeNG `Button` severity="success"): navigates to `/study-notes/:id/quiz`. Pass selected question IDs via router state or a service signal.

Create `src/app/features/study-notes/services/study-notes.service.ts` and `src/app/features/study-notes/services/exams.service.ts` as feature-scoped services (provided in the route's `providers` array, not root).

---

## 6. Feature: Quiz (Estudo de Questões)

**File:** `src/app/features/study-notes/components/quiz/quiz.component.ts`

### State (all signals)

```ts
readonly questions = signal<Question[]>([]);       // received from router state or service
readonly currentIndex = signal(0);
readonly currentQuestion = computed(() => questions()[currentIndex()]);
readonly selectedAnswer = signal<Alternative | ''>('');
readonly hasSubmitted = signal(false);
readonly result = signal<CheckAnswerResponse | null>(null);
readonly isLoading = signal(false);
```

### Layout

- **Header bar:** "Questão X de N" label + navigation buttons (Prev / Next).
- **Question card (PrimeNG `Card`):**
  - Statement text (full, no truncation).
  - Area badge (display `LawArea` as a human-readable label using a `pipe` or a map).
  - Four alternatives (A, B, C, D) as selectable rows. Use PrimeNG `RadioButton` or styled `div` buttons.
    - Alternatives are **disabled** after submission (`hasSubmitted()`).
    - After submission: highlight correct answer in green and selected wrong answer in red.
    - Do **not** reveal correctness before submission.
  - "Confirmar resposta" button: disabled if `selectedAnswer() === ''` or `hasSubmitted()`. On click: call `POST /api/v1/questions/{question_id}/check` with `{ answer: selectedAnswer() }`, set `hasSubmitted(true)` and store the result.
  - After submission: show feedback banner — "Resposta correta!" (green) or "Resposta incorreta." (red) — using PrimeNG `Message`.
- **Navigation:**
  - "Próxima questão" button: resets `selectedAnswer`, `hasSubmitted`, `result`, increments `currentIndex`. Disabled on last question.
  - "Questão anterior" button: same reset + decrements `currentIndex`. Disabled on first question.
  - Direct jump: PrimeNG `Paginator` or a row of numbered buttons to jump to any question by index.

### Loading questions

If questions were passed via router state, use them directly. If the state is empty (e.g. direct URL navigation), show an empty state with a "Voltar" button to `/study-notes`.

---

## 7. Services Summary

| Service | Location | Scope | Endpoints |
|---------|----------|-------|-----------|
| `AuthService` | `core/auth/` | root | `POST /auth/authenticate`, `GET /users/me` |
| `UsersService` | `core/auth/` | root | `POST /users/` |
| `StudyNotesService` | `features/study-notes/services/` | feature | `GET /study-notes/` |
| `ExamsService` | `features/study-notes/services/` | feature | `GET /exams/`, `GET /exams/:id` |
| `QuestionsService` | `features/study-notes/services/` | feature | `GET /questions/exam/:id`, `POST /questions/:id/check` |

All services use `HttpClient` via `inject()`. All HTTP calls use `withCredentials: true` (handled by the interceptor — do not repeat it per-call).

---

## 8. Error Handling Convention

The API returns errors as:
```json
{ "detail": [{ "field": "...", "message": "...", "source": null }] }
```

In services, `catchError` should extract `error.error.detail[0].message` and re-throw as a plain `Error`. Components show the message in a PrimeNG `Toast` (inject `MessageService`, provided in `app.config.ts`).

---

## 9. Checklist Before Reporting Done

- [ ] `ng build` passes with zero errors
- [ ] Auth guard blocks `/study-notes` when not logged in
- [ ] Login sets cookie and stores user in `AuthService`
- [ ] Page refresh restores auth state via `APP_INITIALIZER`
- [ ] Quiz never shows the correct answer before submission
- [ ] All API gaps are marked with `// TODO:` comments
- [ ] No `FormControl` / `FormGroup` / `BehaviorSubject` anywhere
- [ ] Every component has `OnPush`
