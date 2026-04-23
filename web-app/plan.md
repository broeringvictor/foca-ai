# App Shell Navigation — Implementation Plan

## Objective

Build the app shell navigation system:
- Top bar with hamburger trigger
- Left desktop sidebar (fixed, always visible)
- Mobile off-canvas drawer (left-side, overlay)
- Nested menu hierarchy with inline accordion behavior
- Accessible keyboard interactions and focus management

---

## Component Decision

| Role | Component |
|---|---|
| Mobile container | PrimeNG `p-drawer` |
| Nested sidebar nav | PrimeNG `p-panelmenu` (or custom accordion tree) |
| Menu model | Shared typed interface, one source of truth |
| Keyboard / focus | Angular CDK `FocusTrap` + `@HostListener` |

Do **not** use `Dock`, `Menubar`, or floating `Menu` for deep hierarchy.

---

## File Structure

All shell pieces live in `core/layout/` — they are singletons, not feature components.

```
src/app/core/layout/
  layout.service.ts          # drawer state + active route signals
  shell/
    shell.component.ts       # root layout: sidebar + topbar + <router-outlet>
    shell.component.html
  topbar/
    topbar.component.ts
    topbar.component.html
  sidebar/
    sidebar.component.ts     # desktop sidebar, reuses nav-menu
    sidebar.component.html
  nav-menu/
    nav-menu.component.ts    # shared nav tree, used by both sidebar and drawer
    nav-menu.component.html
    nav-menu.model.ts        # NavItem interface
```

The `ShellComponent` wraps all authenticated routes. Wire it in `app.routes.ts` as a layout wrapper with `loadComponent` + `children`.

---

## Shared Menu Model (`nav-menu.model.ts`)

```ts
export interface NavItem {
  label: string;
  icon?: string;          // PrimeIcons key e.g. 'pi pi-home'
  route?: string;         // routerLink target (leaf items only)
  children?: NavItem[];   // nested groups
  sectionLabel?: string;  // rendered as section divider above the item
}
```

The menu data array is a constant — not a service — since it does not change at runtime.

---

## State Management (`layout.service.ts`)

Use signals only. Expose readonly signals; mutate via methods.

```ts
@Injectable({ providedIn: 'root' })
export class LayoutService {
  private _drawerOpen = signal(false);
  readonly drawerOpen = this._drawerOpen.asReadonly();

  // Track expanded panel keys so state survives navigation
  readonly expandedKeys = signal<Record<string, boolean>>({});

  openDrawer()  { this._drawerOpen.set(true);  }
  closeDrawer() { this._drawerOpen.set(false); }
  toggleDrawer(){ this._drawerOpen.update(v => !v); }

  toggleExpanded(key: string) {
    this.expandedKeys.update(keys => ({ ...keys, [key]: !keys[key] }));
  }
}
```

---

## Active Route Detection

Derive the active URL from the Router inside `LayoutService` (or `NavMenuComponent`):

```ts
private router = inject(Router);

readonly activeUrl = toSignal(
  this.router.events.pipe(
    filter(e => e instanceof NavigationEnd),
    map(e => (e as NavigationEnd).urlAfterRedirects)
  ),
  { initialValue: this.router.url }
);

// derived: which NavItem is active
readonly activeRoute = linkedSignal(() =>
  this.activeUrl()  // recomputes on every navigation
);
```

Use `RouterLinkActive` directive in templates for CSS active class binding — do not manage active CSS manually.

---

## Topbar Component

```ts
@Component({
  selector: 'app-topbar',
  templateUrl: './topbar.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ButtonModule],
})
export class TopbarComponent {
  layout = inject(LayoutService);
  // hamburgerBtn used to return focus when drawer closes
  hamburgerBtn = viewChild.required<ElementRef>('hamburgerBtn');
}
```

- Hamburger button: `(click)="layout.toggleDrawer()"` — visible only on mobile (`lg:hidden`).
- Logo/brand in the center or left.
- Right-side actions (theme toggle, user avatar).
- `#hamburgerBtn` template ref captured via `viewChild.required<ElementRef>('hamburgerBtn')`.

---

## Sidebar Component (Desktop)

```ts
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NavMenuComponent],
})
export class SidebarComponent {}
```

- Rendered via `class="hidden lg:flex"` — always in DOM on desktop, hidden via CSS on mobile.
- Fixed left, full height, `w-64`.
- Contains `<app-nav-menu>`.
- No overlay mask needed.

---

## NavMenu Component

```ts
@Component({
  selector: 'app-nav-menu',
  templateUrl: './nav-menu.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PanelMenuModule, RouterLink, RouterLinkActive],
})
export class NavMenuComponent {
  layout = inject(LayoutService);

  // Input: parent (sidebar vs drawer) tells the menu to close on leaf click
  closeOnNavigate = input<boolean>(false);

  readonly menuItems: MenuItem[] = buildPrimeMenuItems(NAV_ITEMS);
}
```

- Map `NavItem[]` → PrimeNG `MenuItem[]` once at module level (`buildPrimeMenuItems`).
- Use `p-panelmenu` for the accordion tree.
- On leaf item click: if `closeOnNavigate()` → `layout.closeDrawer()`.
- Section labels rendered as `<span class="...">` above the group — not interactive.

### PanelMenu PassThrough customization

Avoid direct CSS class overrides. Use the `[pt]` PassThrough API:

```ts
panelMenuPt = {
  root:    { class: 'border-none bg-transparent' },
  panel:   { class: 'border-none' },
  header:  { class: 'rounded-lg hover:bg-[#F3F4F6] text-[#4B5563]' },
  content: { class: 'pl-4' },
};
```

Bind: `<p-panelmenu [pt]="panelMenuPt" ... />`.

---

## Drawer Component (Mobile)

Wire `p-drawer` with the `LayoutService.drawerOpen` signal:

```html
<p-drawer
  [(visible)]="drawerVisible"
  position="left"
  styleClass="p-0 w-64"
  [modal]="true"
  [showCloseIcon]="false"
>
  <app-nav-menu [closeOnNavigate]="true" />
</p-drawer>
```

Because `p-drawer` uses `[(visible)]` (two-way), bridge it with a `model()` signal or use getter/setter:

```ts
get drawerVisible() { return this.layout.drawerOpen(); }
set drawerVisible(v: boolean) { v ? this.layout.openDrawer() : this.layout.closeDrawer(); }
```

### Focus management

- When drawer opens: focus the first focusable element inside it.
- When drawer closes: return focus to the hamburger button.

Use Angular CDK `FocusTrap`:

```ts
private focusTrap = inject(FocusTrapFactory);
private drawerEl = viewChild<ElementRef>('drawerContent');

private readonly manageFocus = effect(() => {
  if (this.layout.drawerOpen()) {
    const trap = this.focusTrap.create(this.drawerEl()!.nativeElement);
    trap.focusInitialElementWhenReady();
  } else {
    this.topbar.hamburgerBtn().nativeElement.focus();
  }
});
```

### Keyboard: Escape closes drawer

```ts
@HostListener('document:keydown.escape')
onEscape() {
  if (this.layout.drawerOpen()) this.layout.closeDrawer();
}
```

---

## Shell Component

```ts
@Component({
  selector: 'app-shell',
  templateUrl: './shell.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterOutlet, TopbarComponent, SidebarComponent, NavMenuComponent, DrawerModule],
})
export class ShellComponent {}
```

```html
<!-- shell.component.html -->
<div class="flex h-screen">
  <!-- Desktop sidebar -->
  <app-sidebar class="hidden lg:flex flex-col w-64 border-r border-[#E5E7EB] bg-white" />

  <!-- Main area -->
  <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
    <app-topbar />
    <main class="flex-1 overflow-y-auto p-4">
      <router-outlet />
    </main>
  </div>
</div>

<!-- Mobile drawer (rendered at root level, outside flex row) -->
<p-drawer [(visible)]="drawerVisible" position="left" ...>
  <app-nav-menu [closeOnNavigate]="true" />
</p-drawer>
```

---

## Layout Behavior

### Desktop

- Sidebar fixed left, full height, `w-64`, `border-r`.
- `p-panelmenu` items expand inline — push content down, no flyouts.
- Expanded state preserved in `LayoutService.expandedKeys`.

### Mobile

- Sidebar hidden (`hidden lg:flex`).
- Hamburger visible in topbar.
- Drawer opens from left with `translateX` transition (PrimeNG handles this).
- Semi-transparent overlay mask: `rgba(15, 23, 42, 0.45)` — provided by `[modal]="true"` on `p-drawer`.
- Click on mask closes drawer (`p-drawer` default behavior).
- Escape key closes drawer (`@HostListener` on `document:keydown.escape`).
- Focus trapped inside drawer while open (CDK FocusTrap).
- Focus returns to hamburger button when closed.
- Navigating to a leaf route closes the drawer.

---

## Visual Rules (Verona Palette)

| Token | Value |
|---|---|
| Menu shell background | `#FFFFFF` |
| Right border divider | `#E5E7EB` |
| Section label text | `#9CA3AF` |
| Default item text | `#4B5563` |
| Default item icon | `#6B7280` |
| Item hover background | `#F3F4F6` |
| Item hover text | `#1F2937` |
| Active item background | `#EEF2FF` |
| Active item text | `#4338CA` |
| Active item icon | `#4F46E5` |
| Chevron muted | `#9CA3AF` |
| Overlay mask | `rgba(15, 23, 42, 0.45)` |
| Focus ring | `#6366F1` |

Apply via Tailwind utility classes or `[pt]` PassThrough where inside PrimeNG internals.
Drawer shell: flush-left, no outer radius. Internal clickable blocks: `rounded-lg` (8px).
Min touch target: `min-h-[44px] min-w-[44px]`.

---

## Accessibility

- `<nav aria-label="Main navigation">` wraps the menu tree.
- Hamburger button: `aria-label="Open navigation"`, `aria-expanded` bound to `layout.drawerOpen()`.
- `p-panelmenu` manages `aria-expanded` on accordion panels natively.
- Keyboard:
  - `Tab` / `Shift+Tab` — focus moves through items.
  - `Enter` / `Space` — activates item or toggles group.
  - `Escape` — closes drawer (handled via `@HostListener`).
- Overlay blocks background interaction while drawer is open (`[modal]="true"`).

---

## Angular 21 Implementation Rules

| Rule | Implementation |
|---|---|
| Standalone components | All shell components standalone; no NgModule |
| OnPush everywhere | `changeDetection: ChangeDetectionStrategy.OnPush` |
| DI via `inject()` | No constructor injection |
| Signal-based state | `signal()`, `computed()`, `linkedSignal()` in `LayoutService` |
| Template refs | `viewChild.required<ElementRef>('ref')` — not `@ViewChild` |
| Router events | `toSignal(router.events.pipe(...))` |
| PrimeNG imports | Imported per-component, never via NgModule style |
| PrimeNG customization | `[pt]` PassThrough API only — no `::ng-deep` |
| DOM side effects | `effect()` or `afterRenderEffect()` — not `ngAfterViewInit` |
| Tailwind layout | Utility classes for all layout/spacing |
| No inline styles | Use Tailwind or PrimeNG PassThrough |
| Dark mode | Already wired via `.dark` class on `<html>` + VioletPreset |

---

## Route Integration

`ShellComponent` wraps all authenticated routes as a layout shell:

```ts
// app.routes.ts
{
  path: '',
  loadComponent: () => import('./core/layout/shell/shell.component').then(m => m.ShellComponent),
  canActivate: [authGuard],
  children: [
    {
      path: 'study-notes',
      loadChildren: () => import('./features/study-notes/study-notes.routes'),
    },
    // other features...
  ],
}
```

---

## Deliverables Checklist

- [ ] `nav-menu.model.ts` — `NavItem` interface + menu data constant
- [ ] `layout.service.ts` — drawer + expanded state signals
- [ ] `TopbarComponent` — hamburger + brand + theme toggle
- [ ] `SidebarComponent` — desktop wrapper, `hidden lg:flex`
- [ ] `NavMenuComponent` — PanelMenu tree, PassThrough styled
- [ ] `ShellComponent` — layout shell + mobile drawer

## Acceptance Criteria

- Desktop sidebar and mobile drawer share the same `NavItem[]` data.
- Mobile drawer opens/closes with overlay mask and full keyboard support.
- Nested submenus expand inline, no flyout popovers.
- Verona visual palette applied via PassThrough and Tailwind utilities.
- All components pass `ng build` with zero type errors.
- Focus trap and return-focus behavior working on drawer open/close.
