// deck-preview.component.ts
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { PanelModule } from 'primeng/panel';
import { DividerModule } from 'primeng/divider';

// Interfaces
import { Card } from '../../models/card.interface';
import { Deck } from '../../models/deck.interface';  // Import Deck interface

@Component({
  selector: 'app-deck-preview',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    TableModule,
    ButtonModule,
    PanelModule,
    DividerModule
  ],
  templateUrl: './deck-preview.component.html',
  styleUrls: ['./deck-preview.component.scss']
})
export class DeckPreviewComponent {
  @Input() deck!: Deck;  // Add input for the entire deck object

  // Computed properties from the deck input
  get deckName(): string {
    return this.deck?.name || 'Unnamed Deck';
  }

  get colors(): string {
    return this.deck?.colors?.join(', ') || 'No colors selected';
  }

  get format(): string {
    return this.deck?.format || 'No format';
  }

  get totalCards(): number {
    return this.deck?.mainboard?.length || 0;
  }

  get averageCmc(): number {
    if (!this.deck?.mainboard) return 0;
    
    const totalCmc = this.deck.mainboard.reduce((sum, card) => {
      // Assuming each card has a manaCost property
      const cmc = parseFloat(card.manaCost) || 0;
      return sum + cmc;
    }, 0);

    return totalCmc / this.totalCards;
  }

  @Input() deckCards: Card[] = [];

  removeCard(card: Card){
    this.deckCards = this.deckCards.filter(c => c.id !== card.id);
  }
}