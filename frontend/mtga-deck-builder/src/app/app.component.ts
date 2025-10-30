import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from './core/services/auth.service';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['app.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive
  ]
})
export class AppComponent {
  title = 'MTGA Deck Builder';
  currentYear = new Date().getFullYear();

  // Observable to track authentication state
  isAuthenticated$: Observable<boolean>;
  username$: Observable<string | null>;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    // Subscribe to auth state changes
    this.isAuthenticated$ = this.authService.authState$.pipe(
      map(state => state.user !== null && state.token !== null)
    );

    this.username$ = this.authService.currentUser$.pipe(
      map(user => user?.username || null)
    );
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}