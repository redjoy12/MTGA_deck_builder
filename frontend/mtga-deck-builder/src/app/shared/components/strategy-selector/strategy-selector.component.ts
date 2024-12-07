// strategy-selector.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';

@Component({
  selector: 'app-strategy-selector',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    ButtonModule,
    DialogModule
  ],
  templateUrl: './strategy-selector.component.html',
  styleUrls: ['./strategy-selector.component.scss']
})
export class StrategySelectorComponent {
  strategies = [
    { 
      name: 'Aggro', 
      description: 'Fast-paced strategy focused on dealing damage quickly',
      details: ['Low mana curve', 'Many cheap creatures', 'Direct damage spells']
    },
    { 
      name: 'Control', 
      description: 'Strategy focused on controlling the game and outlasting opponents',
      details: ['Counterspells and removal', 'Card draw and resource generation', 'Late-game win conditions']
    }
  ];

  selectedStrategy: any;
  displayDialog: boolean = false;

  showDetails(strategy: any) {
    this.selectedStrategy = strategy;
    this.displayDialog = true;
  }

  closeDialog() {
    this.displayDialog = false;
  }
}