import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { TabViewModule } from 'primeng/tabview';
import { DialogModule } from 'primeng/dialog';
import { MultiSelectModule } from 'primeng/multiselect';
import { TableModule } from 'primeng/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet, 
    RouterLink, 
    RouterLinkActive,
    
    // PrimeNG Modules
    CardModule,
    ButtonModule,
    InputTextModule,
    DropdownModule,
    TabViewModule,
    DialogModule,
    MultiSelectModule,
    TableModule,
    
    // Forms
    FormsModule,
    ReactiveFormsModule
  ],
  template: `
    <div class="app-container">
      <header>
        <nav>
          <ul>
            <li>
              <a routerLink="/deck-creator" routerLinkActive="active">
                Deck Creator
              </a>
            </li>
            <li>
              <a routerLink="/card-selector" routerLinkActive="active">
                Card Selector
              </a>
            </li>
            <li>
              <a routerLink="/deck-preview" routerLinkActive="active">
                Deck Preview
              </a>
            </li>
            <li>
              <a routerLink="/resource-manager" routerLinkActive="active">
                Resource Manager
              </a>
            </li>
          </ul>
        </nav>
      </header>

      <main>
        <router-outlet></router-outlet>
      </main>

      <footer>
        <p>&copy; {{ currentYear }} MTGA Deck Builder</p>
      </footer>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    
    header {
      background-color: #333;
      color: white;
      padding: 1rem;
    }
    
    nav ul {
      display: flex;
      list-style: none;
      gap: 1rem;
    }
    
    nav a {
      color: white;
      text-decoration: none;
    }
    
    nav a.active {
      font-weight: bold;
      text-decoration: underline;
    }
    
    main {
      flex-grow: 1;
      padding: 1rem;
    }
    
    footer {
      background-color: #333;
      color: white;
      text-align: center;
      padding: 1rem;
    }
  `]
})
export class AppComponent {
  title = 'MTGA Deck Builder';
  currentYear = new Date().getFullYear();
}