---
name: angular-tailwind-setup
description: Set up Tailwind CSS v4 in an Angular project with PostCSS, custom theming, dark mode, and PrimeNG integration
version: 1.0.0
license: MIT
---

# Tailwind CSS v4 Setup for Angular

This guide covers setting up Tailwind CSS v4 in an Angular project (v17+) using PostCSS. No `tailwind.config.js` is needed — configuration is CSS-first.

## Overview

This setup uses:

- **Tailwind CSS v4** — CSS-first configuration via `@theme`
- **@tailwindcss/postcss** — PostCSS plugin for Tailwind v4
- **postcss** — Build tool integration

## Installation

```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

Do **not** install `autoprefixer` — the Angular build pipeline handles vendor prefixes.

## Configuration Files

### PostCSS Config

Create `.postcssrc.json` in the project root (next to `angular.json`):

```json
{
  "plugins": {
    "@tailwindcss/postcss": {}
  }
}
```

Do **NOT** create a `tailwind.config.js`. Tailwind v4 is configured entirely through CSS.

### Global Styles

In `src/styles.css`, add the Tailwind import as the first line:

```css
@import 'tailwindcss';
```

If using SCSS (`src/styles.scss`), use:

```scss
@use 'tailwindcss';
```

That's all the setup needed. No `@tailwind base/components/utilities` directives — those are Tailwind v3 syntax and will break the build.

## Custom Theme Variables

Customize the design system by adding an `@theme` block in `src/styles.css`:

```css
@import 'tailwindcss';

@theme {
  /* Brand colors */
  --color-primary: #6366f1;
  --color-primary-dark: #4f46e5;
  --color-secondary: #f59e0b;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Custom spacing */
  --spacing-18: 4.5rem;
  --spacing-22: 5.5rem;

  /* Border radius */
  --radius-card: 0.75rem;
}
```

Use them as Tailwind utilities in templates:

```html
<div class="bg-primary text-white rounded-card p-4">
  <p class="font-sans text-sm">Hello Tailwind!</p>
</div>
```

## Dark Mode

Tailwind v4 uses CSS media queries for dark mode by default. To use class-based dark mode instead, add to `src/styles.css`:

```css
@import 'tailwindcss';

@variant dark (&:where(.dark, .dark *));
```

Then toggle by adding/removing the `dark` class on `<html>` or a wrapper element:

```ts
// In a ThemeService
toggleDark() {
  document.documentElement.classList.toggle('dark');
}
```

## Angular Component Encapsulation

Tailwind utility classes work best with `ViewEncapsulation.None` or directly in component templates. By default, Angular scopes component styles — Tailwind classes in `styles` or `styleUrl` will be scoped and may not apply globally.

**Recommended approach:** Use Tailwind only in templates (HTML). Keep component-specific overrides in `styles`/`styleUrl` with Angular's default encapsulation.

```ts
@Component({
  selector: 'app-card',
  template: `<div class="rounded-xl bg-white shadow-md p-6">...</div>`,
  // No styleUrl needed for Tailwind-only components
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CardComponent {}
```

If you need global styles from a component (e.g., third-party overrides), set:

```ts
@Component({
  encapsulation: ViewEncapsulation.None,
  styleUrl: './my.component.css',
})
```

## PrimeNG Integration

When using PrimeNG alongside Tailwind, add the following to `src/styles.css` to prevent conflicts:

```css
@import 'tailwindcss';

/* Disable Tailwind's preflight (reset) to avoid breaking PrimeNG base styles */
@layer base {
  /* Intentionally empty — preflight disabled for PrimeNG compatibility */
}
```

Or, use Tailwind's `@layer` to scope resets away from PrimeNG components:

```css
@import 'tailwindcss';

/* Use Tailwind for layout/spacing, PrimeNG for component theming */
```

Use the PassThrough (`pt`) API on PrimeNG components to inject Tailwind classes without overriding internal styles:

```ts
import { ButtonModule } from 'primeng/button';

// In component template:
// <p-button [pt]="{ root: 'rounded-xl' }" label="Click me" />
```

## Utility Helpers

### cn() — Conditional Class Merging

Install `clsx` and `tailwind-merge` for safe class merging:

```bash
npm install clsx tailwind-merge
```

Create `src/app/shared/utils/cn.ts`:

```ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
```

Usage in components:

```ts
import { cn } from '@/shared/utils/cn';

@Component({
  template: `
    <button [class]="buttonClass()">Click</button>
  `,
})
export class ButtonComponent {
  variant = input<'primary' | 'ghost'>('primary');

  buttonClass = computed(() => cn(
    'rounded-lg px-4 py-2 font-medium transition',
    this.variant() === 'primary' && 'bg-primary text-white hover:bg-primary-dark',
    this.variant() === 'ghost' && 'bg-transparent text-primary hover:bg-primary/10',
  ));
}
```

## Responsive Design

Tailwind v4 breakpoints work the same way — use responsive prefixes in templates:

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="p-4">Item</div>
</div>
```

## Key Differences from Tailwind v3

| v3 (DO NOT USE) | v4 (correct) |
|---|---|
| `tailwind.config.js` | `@theme {}` in CSS |
| `@tailwind base` | `@import 'tailwindcss'` |
| `@tailwind utilities` | included in `@import` |
| `theme.extend.colors` | `--color-* vars in @theme` |
| `darkMode: 'class'` in config | `@variant dark` in CSS |

## Troubleshooting

### Classes not applying

1. Verify `.postcssrc.json` exists at the project root (same level as `angular.json`).
2. Confirm `@import 'tailwindcss'` is the first line in `src/styles.css`.
3. Run `ng build` — PostCSS errors appear in the build output.
4. Make sure `tailwindcss` and `@tailwindcss/postcss` are in `devDependencies`.

### PrimeNG styles broken after adding Tailwind

Tailwind's preflight (CSS reset) can conflict with PrimeNG. Disable it by not using `@layer base` overrides, or scope resets to non-PrimeNG elements.

### `tailwind.config.js` not found error

You should NOT have a `tailwind.config.js`. If an error references it, delete the file — v4 does not use it.

### Angular build ignores PostCSS

Ensure you are using `@angular/build` (not the legacy `@angular-devkit/build-angular` Webpack builder). The Vite-based builder picks up `.postcssrc.json` automatically.
