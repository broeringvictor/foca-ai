import { Component, ChangeDetectionStrategy, inject, input } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { NAV_ITEMS, NavItem } from './nav-menu.model';
import { LayoutService } from '../layout.service';

@Component({
  selector: 'app-nav-menu',
  templateUrl: './nav-menu.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, RouterLinkActive, ButtonModule, TooltipModule],
})
export class NavMenuComponent {
  closeOnNavigate = input<boolean>(false);
  iconOnly = input<boolean>(false);

  private layout = inject(LayoutService);

  readonly items: NavItem[] = NAV_ITEMS;

  linkClass(isActive: boolean): string {
    if (this.iconOnly()) {
      return isActive
        ? 'flex h-16 w-16 items-center justify-center rounded-full border border-primary/15 bg-primary/10 shadow-sm shadow-primary/10 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-primary'
        : 'flex h-16 w-16 items-center justify-center rounded-full border border-transparent transition-colors outline-none hover:bg-slate-100 focus-visible:ring-2 focus-visible:ring-primary dark:hover:bg-white/10';
    }

    return isActive
      ? 'flex items-center gap-3 rounded-lg min-h-[44px] px-3 bg-primary/10 text-primary transition-colors outline-none focus-visible:ring-2 focus-visible:ring-primary'
      : 'flex items-center gap-3 rounded-lg min-h-[44px] px-3 text-surface-600 transition-colors outline-none hover:bg-surface-100 hover:text-surface-900 focus-visible:ring-2 focus-visible:ring-primary dark:text-surface-700 dark:hover:bg-white/10 dark:hover:text-surface-950';
  }

  onLeafClick(): void {
    if (this.closeOnNavigate()) this.layout.closeDrawer();
  }
}
