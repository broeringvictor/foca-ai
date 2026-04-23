import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class LayoutService {
  private _drawerOpen = signal(false);
  readonly drawerOpen = this._drawerOpen.asReadonly();

  openDrawer()   { this._drawerOpen.set(true);  }
  closeDrawer()  { this._drawerOpen.set(false); }
  toggleDrawer() { this._drawerOpen.update(v => !v); }
}
