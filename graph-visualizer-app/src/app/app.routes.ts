import {Routes} from '@angular/router';
import {MainShell} from './components/main/main-shell';

export const routes: Routes = [
  {
    path: '',
    component: MainShell,
  },
  {
    path: '**',
    redirectTo: '',
  }
];
