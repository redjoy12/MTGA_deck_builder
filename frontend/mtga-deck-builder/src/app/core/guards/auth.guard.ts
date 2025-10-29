import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Auth Guard - Protects routes that require authentication
 *
 * This guard checks if the user is authenticated before allowing access to a route.
 * If the user is not authenticated, they are redirected to the login page.
 *
 * Usage in routes:
 * {
 *   path: 'protected-route',
 *   component: ProtectedComponent,
 *   canActivate: [authGuard]
 * }
 */
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Check if user is authenticated
  if (authService.isAuthenticated()) {
    return true;
  }

  // Not authenticated, redirect to login page with return url
  router.navigate(['/login'], {
    queryParams: { returnUrl: state.url }
  });

  return false;
};

/**
 * Guest Guard - Prevents authenticated users from accessing auth pages
 *
 * This guard checks if the user is authenticated and redirects them to the deck creator
 * if they try to access login or register pages while already logged in.
 *
 * Usage in routes:
 * {
 *   path: 'login',
 *   component: LoginComponent,
 *   canActivate: [guestGuard]
 * }
 */
export const guestGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Check if user is authenticated
  if (!authService.isAuthenticated()) {
    return true;
  }

  // Already authenticated, redirect to deck creator
  router.navigate(['/deck-creator']);

  return false;
};
