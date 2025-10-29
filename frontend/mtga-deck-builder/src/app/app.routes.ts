import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  // Authentication routes (accessible only when not logged in)
  {
    path: 'login',
    loadComponent: () => import('./auth/login/login.component').then(m => m.LoginComponent),
    canActivate: [guestGuard]
  },
  {
    path: 'register',
    loadComponent: () => import('./auth/register/register.component').then(m => m.RegisterComponent),
    canActivate: [guestGuard]
  },

  // Protected routes (require authentication)
  {
    path: 'deck-creator',
    loadComponent: () => import('./pages/deck-creator/deck-creator.component').then(m => m.DeckCreatorComponent),
    canActivate: [authGuard]
  },
  {
    path: 'card-selector',
    loadComponent: () => import('./pages/card-selector/card-selector.component').then(m => m.CardSelectorComponent),
    canActivate: [authGuard]
  },
  {
    path: 'deck-preview',
    loadComponent: () => import('./pages/deck-preview/deck-preview.component').then(m => m.DeckPreviewComponent),
    canActivate: [authGuard]
  },
  {
    path: 'resource-manager',
    loadComponent: () => import('./pages/resource-manager/resource-manager.component').then(m => m.ResourceManagerComponent),
    canActivate: [authGuard]
  },

  // Default redirect
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },

  // Wildcard route for 404
  {
    path: '**',
    redirectTo: '/login'
  }
];