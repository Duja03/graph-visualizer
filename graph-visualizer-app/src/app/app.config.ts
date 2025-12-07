import {ApplicationConfig, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection} from '@angular/core';
import {provideRouter, RouterLink, RouterLinkActive, RouterOutlet} from '@angular/router';

import {routes} from './app.routes';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatButtonModule} from '@angular/material/button';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatInputModule} from "@angular/material/input";
import {MatTreeModule} from '@angular/material/tree';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatDatepickerModule} from '@angular/material/datepicker';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatChipsModule} from '@angular/material/chips';
import {MatGridListModule} from '@angular/material/grid-list';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatTabsModule} from '@angular/material/tabs';
import {MatTableModule} from '@angular/material/table';
import {MatCardModule} from '@angular/material/card';
import {MatDialogModule} from '@angular/material/dialog';
import {MatSortModule} from '@angular/material/sort';
import {MatRadioModule} from '@angular/material/radio';
import {MatDividerModule} from '@angular/material/divider';
import {MatMenuModule} from '@angular/material/menu';
import {MatIconModule} from '@angular/material/icon';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatSelectModule} from '@angular/material/select';
import {MatTooltipModule} from '@angular/material/tooltip';
import {CommonModule} from '@angular/common';
import {ReactiveFormsModule} from '@angular/forms';
import {RestConfig} from './rest/rest.config';
import {environment} from '../main';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes)
  ]
};

export function restConfigFactory(): RestConfig {
  const { config } = environment;

  if (!config?.rest) {
    throw 'You must provide rest configuration via config.yaml';
  }

  return config.rest;
}

export const angularComponents = [
  MatButtonModule,
  MatCheckboxModule,
  MatToolbarModule,
  MatMenuModule,
  MatFormFieldModule,
  MatTooltipModule,
  MatSidenavModule,
  MatTabsModule,
  MatTableModule,
  MatIconModule,
  MatCardModule,
  MatSelectModule,
  MatDialogModule,
  MatSortModule,
  MatRadioModule,
  MatDividerModule,
  MatToolbarModule,
  MatInputModule,
  MatProgressBarModule,
  MatProgressSpinnerModule,
  MatTreeModule,
  MatExpansionModule,
  MatDatepickerModule,
  MatAutocompleteModule,
  MatChipsModule,
  MatGridListModule,
  MatPaginatorModule,
];

export const shared = [
  ...angularComponents,
  ReactiveFormsModule,
  CommonModule,
  RouterLink,
  RouterOutlet,
  RouterLinkActive,
];
