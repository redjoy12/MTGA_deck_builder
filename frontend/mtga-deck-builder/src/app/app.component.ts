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
  templateUrl: './app.component.html',
  styleUrls: ['app.component.scss'],
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
  ]
})
export class AppComponent {
  title = 'MTGA Deck Builder';
  currentYear = new Date().getFullYear();
}