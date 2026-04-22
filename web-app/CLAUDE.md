# Angular 21 + PrimeNG + Tailwind v4 — Architecture Guidelines

## Rendering

This is a **Client-Side Rendering (CSR) only** app. Do not add SSR, SSG, or prerendering. Never use `provideServerRendering()`, `@angular/ssr`, or `TransferState`.

## Stack

- **Angular 21** — standalone components, signals, `@angular/forms/signals`
- **PrimeNG** — UI component library (import individual modules, never NgModule-style)
- **Tailwind CSS v4** — utility-first styling via `@import 'tailwindcss'` in `styles.css`
- **TypeScript ~5.9**, **Vitest** for unit tests

## Project Structure

```
src/
  app/
    core/               # App-wide singletons: auth, http, guards, interceptors
      auth/
      http/
    shared/             # Reusable UI: dumb components, directives, pipes, utils
      components/
      directives/
      pipes/
    features/           # Feature modules (lazy-loaded via router)
      <feature>/
        components/     # Smart + dumb components for this feature
        services/       # Feature-scoped services
        <feature>.routes.ts
    app.config.ts
    app.routes.ts       # Top-level routes (lazy-loads features)
```

- One feature per folder. Features are self-contained.
- `core/` services are app singletons (`providedIn: 'root'`).
- `shared/` has no feature knowledge — no imports from `features/`.

## Components

- Always **standalone** (`standalone: true` is default in Angular 19+, no need to set it).
- Always `changeDetection: ChangeDetectionStrategy.OnPush`.
- Use `inject()` instead of constructor injection.
- Prefer `input()` / `output()` signal-based APIs over `@Input()` / `@Output()`.
- Separate template files for non-trivial components (`templateUrl`).

```ts
import { Component, ChangeDetectionStrategy, inject, input, output } from '@angular/core';

@Component({
  selector: 'app-card',
  templateUrl: './card.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CardComponent {
  title = input.required<string>();
  dismissed = output<void>();

  private someService = inject(SomeService);
}
```

## Reactivity — Signals

Use Signals for all state. Never use `BehaviorSubject` for component state.

```ts
import { signal, computed, effect } from '@angular/core';

readonly count = signal(0);
readonly doubled = computed(() => this.count() * 2);
```

- Services expose state as `readonly` signals: `readonly items = this._items.asReadonly()`.
- `effect()` is only for side effects (DOM manipulation, logging). Do **not** use it to sync signals to other signals — use `computed` or `linkedSignal` instead.
- For async data fetching, use `resource()`:

```ts
import { resource, signal } from '@angular/core';

readonly userId = signal(1);
readonly user = resource({
  params: this.userId,
  loader: async ({ params: id }) => this.userService.fetchById(id),
});
```

## Forms — Signal Forms (Angular 21)

**Always use Signal Forms** (`@angular/forms/signals`). Never use `FormControl`, `FormGroup`, or `FormBuilder`.

```ts
import { form, FormField, submit, required, email } from '@angular/forms/signals';
import { signal } from '@angular/core';

model = signal({ name: '', email: '' }); // NEVER use null — use '' or 0 or []

userForm = form(this.model, (s) => {
  required(s.name, { message: 'Name is required' });
  required(s.email);
  email(s.email, { message: 'Invalid email' });
});

onSubmit() {
  submit(this.userForm, async () => {
    await this.apiService.save(this.model());
  });
}
```

**Critical Signal Forms rules:**
- Access field state by calling it: `form.field().valid()`, NOT `form.field.valid()`.
- Root form flags: `form().invalid()`, NOT `form.invalid()`.
- Never set `null`/`undefined` as initial signal values. Use `''`, `0`, `[]`, or `false`.
- Never bind `min`, `max`, `value`, `[disabled]`, or `[readonly]` as HTML attributes on `[formField]` inputs — use schema rules instead.
- `submit()` callback **must** be `async`.
- Template binding: `<input [formField]="userForm.name" />`.
- Disable submit: `<button [disabled]="userForm().invalid()">`.

## Services & Dependency Injection

```ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
}
```

- Use `inject()` at class field level (not inside methods).
- Feature-scoped services are provided in the route's `providers` array, not at root.
- Never use `NgModule` providers.

## Routing

All feature routes are lazy-loaded:

```ts
// app.routes.ts
export const routes: Routes = [
  {
    path: 'dashboard',
    loadChildren: () => import('./features/dashboard/dashboard.routes'),
  },
];
```

- Use `CanMatchFn` / `CanActivateFn` functional guards (not class-based guards).
- Use `ResolveFn` for pre-fetching data.
- Prefer `loadComponent` for single-component routes, `loadChildren` for feature route groups.

## PrimeNG Integration

Import PrimeNG components directly into the `imports` array of standalone components.

```ts
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';

@Component({
  imports: [ButtonModule, TableModule],
  // ...
})
```

- Use `providePrimeNG()` and `provideAnimationsAsync()` in `app.config.ts`.
- Apply the PrimeNG theme in `app.config.ts`, NOT in styles.
- Use Tailwind utilities for layout and spacing around PrimeNG components.
- Avoid overriding PrimeNG internal CSS directly — use `pt` (PassThrough) API for customization.

```ts
// app.config.ts
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideAnimationsAsync(),
    providePrimeNG({ theme: { preset: Aura } }),
  ],
};
```

## Tailwind CSS v4

- Global import: `@import 'tailwindcss';` in `src/styles.css` — no other setup needed.
- Do **not** create `tailwind.config.js` (v4 uses CSS variables).
- Do **not** use `@tailwind base/components/utilities` directives.
- Customize via CSS `@theme` block in `styles.css` if needed.

```css
/* src/styles.css */
@import 'tailwindcss';

@theme {
  --color-primary: #6366f1;
}
```

## Code Generation

Use Angular CLI for all scaffolding:

```bash
ng generate component features/dashboard/components/user-list
ng generate service features/dashboard/services/user
ng generate guard core/auth/auth
```

Always run `ng build` after generating to catch type errors before committing.

## Testing

- Unit tests with **Vitest** + Angular's `TestBed`.
- File naming: `*.spec.ts` alongside the file under test.
- Use `TestBed.configureTestingModule` with `imports` (standalone components).
- Prefer testing behavior over implementation details.
- For routing tests, use `RouterTestingHarness`.

## Key Rules (Never Break)

| Rule | Reason |
|------|--------|
| `OnPush` on every component | Prevents unnecessary change detection |
| Signal Forms only | No `FormControl`/`FormGroup` in this codebase |
| `inject()` over constructor | Angular 21 idiomatic DI |
| Standalone only | No `NgModule` declarations |
| Tailwind v4 patterns | v3 patterns (`tailwind.config.js`) break the build |
| Lazy load all features | Bundle size and load time |
| `null`-free signal models | Signal Forms requires non-null initial values |
