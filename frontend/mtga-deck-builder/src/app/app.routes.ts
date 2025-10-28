import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'deck-creator',
    loadComponent: () => import('./pages/deck-creator/deck-creator.component').then(m => m.DeckCreatorComponent)
  },
  {
    path: 'card-selector',
    loadComponent: () => import('./pages/card-selector/card-selector.component').then(m => m.CardSelectorComponent)
  },
  {
    path: 'deck-preview',
    loadComponent: () => import('./pages/deck-preview/deck-preview.component').then(m => m.DeckPreviewComponent)
  },
  {
    path: 'resource-manager',
    loadComponent: () => import('./pages/resource-manager/resource-manager.component').then(m => m.ResourceManagerComponent)
  },
  {
    path: '',
    redirectTo: '/deck-creator',
    pathMatch: 'full'
  }
];