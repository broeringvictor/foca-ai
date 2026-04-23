import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
  effect,
  viewChild,
  ElementRef,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { LayoutService } from '../layout.service';

type ThemeMode = 'light' | 'dark';
const THEME_STORAGE_KEY = 'foca-theme-mode';

@Component({
  selector: 'app-topbar',
  templateUrl: './topbar.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, ButtonModule, TooltipModule],
})
export class TopbarComponent {
  layout = inject(LayoutService);

  readonly hamburgerBtn = viewChild<ElementRef>('hamburgerBtn');

  readonly theme = signal<ThemeMode>(this.readStoredTheme());
  readonly isDark = computed(() => this.theme() === 'dark');

  private readonly syncTheme = effect(() => {
    const theme = this.theme();
    const root = document.documentElement;
    root.classList.toggle('dark', theme === 'dark');
    root.classList.toggle('light', theme === 'light');
    root.style.colorScheme = theme;
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  });

  toggleDarkMode(): void {
    this.theme.update(t => (t === 'dark' ? 'light' : 'dark'));
  }

  private readStoredTheme(): ThemeMode {
    return localStorage.getItem(THEME_STORAGE_KEY) === 'dark' ? 'dark' : 'light';
  }
}
