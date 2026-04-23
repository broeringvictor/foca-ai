import { Component, ChangeDetectionStrategy } from '@angular/core';
import { NavMenuComponent } from '../nav-menu/nav-menu.component';

@Component({
  selector: 'app-sidebar',
  template: `<app-nav-menu [iconOnly]="true" />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NavMenuComponent],
  host: {
    class: 'hidden lg:flex flex-col w-20 shrink-0 overflow-y-auto pt-3 bg-surface-0 dark:bg-surface-0',
  },
})
export class SidebarComponent {}
