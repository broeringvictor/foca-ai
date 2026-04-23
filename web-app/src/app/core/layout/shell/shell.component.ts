import {
  Component,
  ChangeDetectionStrategy,
  inject,
  viewChild,
  effect,
  HostListener,
} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { DrawerModule } from 'primeng/drawer';
import { LayoutService } from '../layout.service';
import { TopbarComponent } from '../topbar/topbar.component';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { NavMenuComponent } from '../nav-menu/nav-menu.component';

@Component({
  selector: 'app-shell',
  templateUrl: './shell.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterOutlet, DrawerModule, TopbarComponent, SidebarComponent, NavMenuComponent],
})
export class ShellComponent {
  layout = inject(LayoutService);

  private topbar = viewChild.required(TopbarComponent);

  private wasDrawerOpen = false;

  private readonly returnFocus = effect(() => {
    const isOpen = this.layout.drawerOpen();
    if (this.wasDrawerOpen && !isOpen) {
      queueMicrotask(() => this.topbar().hamburgerBtn()?.nativeElement.focus());
    }
    this.wasDrawerOpen = isOpen;
  });

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (this.layout.drawerOpen()) this.layout.closeDrawer();
  }

  onDrawerHide(): void {
    this.layout.closeDrawer();
  }
}
